#include <stdio.h>
#include <string.h>

#include "libhirte/bus/peer-bus.h"
#include "libhirte/bus/user-bus.h"
#include "libhirte/common/common.h"
#include "libhirte/common/parse-util.h"
#include "libhirte/ini/config.h"
#include "libhirte/service/shutdown.h"
#include "libhirte/socket.h"

#include "manager.h"
#include "node.h"

#define DEBUG_MESSAGES 0

Manager *manager_new(void) {
        fprintf(stdout, "Creating Manager...\n");

        int r = 0;
        _cleanup_sd_event_ sd_event *event = NULL;
        r = sd_event_default(&event);
        if (r < 0) {
                fprintf(stderr, "Failed to create event loop: %s\n", strerror(-r));
                return NULL;
        }

        _cleanup_free_ char *service_name = strdup(HIRTE_DBUS_NAME);
        if (service_name == NULL) {
                fprintf(stderr, "Out of memory\n");
                return NULL;
        }

        Manager *manager = malloc0(sizeof(Manager));
        if (manager != NULL) {
                manager->port = HIRTE_DEFAULT_PORT;
                manager->user_bus_service_name = steal_pointer(&service_name);
                manager->event = steal_pointer(&event);
                LIST_HEAD_INIT(manager->nodes);
        }

        return manager;
}

Manager *manager_ref(Manager *manager) {
        manager->ref_count++;
        return manager;
}

void manager_unref(Manager *manager) {
        manager->ref_count--;
        if (manager->ref_count != 0) {
                return;
        }

        if (manager->event != NULL) {
                sd_event_unrefp(&manager->event);
        }

        free(manager->user_bus_service_name);

        if (manager->node_connection_source != NULL) {
                sd_event_source_unrefp(&manager->node_connection_source);
        }

        if (manager->manager_slot != NULL) {
                sd_bus_slot_unref(manager->manager_slot);
        }

        if (manager->user_dbus != NULL) {
                sd_bus_unrefp(&manager->user_dbus);
        }

        Node *node = NULL;
        LIST_FOREACH(nodes, node, manager->nodes) {
                node_unref(node);
        }
        LIST_FOREACH(nodes, node, manager->anonymous_nodes) {
                node_unref(node);
        }


        free(manager);
}

void manager_unrefp(Manager **managerp) {
        if (managerp && *managerp) {
                manager_unref(*managerp);
                *managerp = NULL;
        }
}

Node *manager_find_node(Manager *manager, const char *name) {
        Node *node = NULL;

        LIST_FOREACH(nodes, node, manager->nodes) {
                if (strcmp(node->name, name) == 0) {
                        return node;
                }
        }

        return NULL;
}

void manager_remove_node(Manager *manager, Node *node) {
        if (node->name) {
                manager->n_nodes--;
                LIST_REMOVE(nodes, manager->nodes, node);
        } else {
                LIST_REMOVE(nodes, manager->anonymous_nodes, node);
        }
        node_unref(node);
}

Node *manager_add_node(Manager *manager, const char *name) {
        _cleanup_node_ Node *node = node_new(manager, name);
        if (node == NULL) {
                return NULL;
        }

        if (name) {
                manager->n_nodes++;
                LIST_APPEND(nodes, manager->nodes, node);
        } else {
                LIST_APPEND(nodes, manager->anonymous_nodes, node);
        }

        return steal_pointer(&node);
}

bool manager_set_port(Manager *manager, const char *port_s) {
        uint16_t port = 0;

        if (!parse_port(port_s, &port)) {
                fprintf(stderr, "Invalid port format '%s'\n", port_s);
                return false;
        }
        manager->port = port;
        return true;
}

bool manager_parse_config(Manager *manager, const char *configfile) {
        _cleanup_config_ config *config = NULL;
        topic *topic = NULL;
        const char *port = NULL;

        config = parsing_ini_file(configfile);
        if (config == NULL) {
                return false;
        }

        print_all_topics(config);

        topic = config_lookup_topic(config, "Manager");
        if (topic == NULL) {
                return true;
        }

        port = topic_lookup(topic, "Port");
        if (port) {
                if (!manager_set_port(manager, port)) {
                        return false;
                }
        }

        const char *expected_nodes = topic_lookup(topic, "Nodes");
        if (expected_nodes) {
                char *saveptr = NULL;
                char *name = strtok_r((char *) expected_nodes, ",", &saveptr);
                while (name != NULL) {
                        if (manager_find_node(manager, name) == NULL) {
                                manager_add_node(manager, name);
                        }

                        name = strtok_r(NULL, ",", &saveptr);
                }
        }

        /* TODO: Handle per-node-name option section */

        return true;
}

static int manager_accept_node_connection(
                UNUSED sd_event_source *source, int fd, UNUSED uint32_t revents, void *userdata) {
        Manager *manager = userdata;
        Node *node = NULL;
        _cleanup_fd_ int nfd = accept_tcp_connection_request(fd);

        if (nfd < 0) {
                return -1;
        }

        _cleanup_sd_bus_ sd_bus *dbus_server = peer_bus_open_server(
                        manager->event, "managed-node", HIRTE_DBUS_NAME, steal_fd(&nfd));
        if (dbus_server == NULL) {
                return -1;
        }

        /* Add anonymous node */
        node = manager_add_node(manager, NULL);
        if (node == NULL) {
                return -1;
        }

        if (!node_set_agent_bus(node, dbus_server)) {
                manager_remove_node(manager, steal_pointer(&node));
                return -1;
        }

        return 0;
}

static bool manager_setup_node_connection_handler(Manager *manager) {
        int r = 0;
        _cleanup_sd_event_source_ sd_event_source *event_source = NULL;

        _cleanup_fd_ int accept_fd = create_tcp_socket(manager->port);
        if (accept_fd < 0) {
                return false;
        }

        r = sd_event_add_io(
                        manager->event, &event_source, accept_fd, EPOLLIN, manager_accept_node_connection, manager);
        if (r < 0) {
                fprintf(stderr, "Failed to add io event: %s\n", strerror(-r));
                return false;
        }
        r = sd_event_source_set_io_fd_own(event_source, true);
        if (r < 0) {
                fprintf(stderr, "Failed to set io fd own: %s\n", strerror(-r));
                return false;
        }

        // sd_event_set_io_fd_own takes care of closing accept_fd
        steal_fd(&accept_fd);

        (void) sd_event_source_set_description(event_source, "node-accept-socket");

        manager->node_connection_source = steal_pointer(&event_source);

        return true;
}

/* This is a test method for now, it just returns what you passed */
static int manager_method_ping(sd_bus_message *m, UNUSED void *userdata, UNUSED sd_bus_error *ret_error) {
        const char *arg = NULL;

        int r = sd_bus_message_read(m, "s", &arg);
        if (r < 0) {
                return r;
        }

        return sd_bus_reply_method_return(m, "s", arg);
}

typedef struct ListUnitsRequest {
        sd_bus_message *request_message;

        int n_done;
        int n_sub_req;
        struct {
                Node *node;
                sd_bus_message *m;
                AgentRequest *agent_req;
        } sub_req[0];
} ListUnitsRequest;

static void list_unit_request_free(ListUnitsRequest *req) {
        sd_bus_message_unref(req->request_message);

        for (int i = 0; i < req->n_sub_req; i++) {
                if (req->sub_req[i].node) {
                        node_unref(req->sub_req[i].node);
                }
                if (req->sub_req[i].m) {
                        sd_bus_message_unref(req->sub_req[i].m);
                }
                if (req->sub_req[i].agent_req) {
                        agent_request_unref(req->sub_req[i].agent_req);
                }
        }

        free(req);
}

void list_unit_request_freep(ListUnitsRequest **reqp) {
        if (reqp && *reqp) {
                list_unit_request_free(*reqp);
                *reqp = NULL;
        }
}

#define _cleanup_list_unit_request_ _cleanup_(list_unit_request_freep)


static int manager_method_list_units_encode_reply(ListUnitsRequest *req, sd_bus_message *reply) {
        int r = sd_bus_message_open_container(reply, SD_BUS_TYPE_ARRAY, "(sssssssouso)");
        if (r < 0) {
                return r;
        }

        for (int i = 0; i < req->n_sub_req; i++) {
                const char *node_name = req->sub_req[i].node->name;
                sd_bus_message *m = req->sub_req[i].m;
                if (m == NULL) {
                        continue;
                }

                r = sd_bus_message_enter_container(m, SD_BUS_TYPE_ARRAY, "(ssssssouso)");
                if (r < 0) {
                        return r;
                }

                while (sd_bus_message_at_end(m, false) == 0) {
                        r = sd_bus_message_open_container(reply, SD_BUS_TYPE_STRUCT, "sssssssouso");
                        if (r < 0) {
                                return r;
                        }
                        r = sd_bus_message_enter_container(m, SD_BUS_TYPE_STRUCT, "ssssssouso");
                        if (r < 0) {
                                return r;
                        }

                        r = sd_bus_message_append(reply, "s", node_name);
                        if (r < 0) {
                                return r;
                        }
                        r = sd_bus_message_copy(reply, m, true);
                        if (r < 0) {
                                return r;
                        }

                        r = sd_bus_message_close_container(reply);
                        if (r < 0) {
                                return r;
                        }
                        r = sd_bus_message_exit_container(m);
                        if (r < 0) {
                                return r;
                        }
                }

                r = sd_bus_message_exit_container(m);
                if (r < 0) {
                        return r;
                }
        }

        r = sd_bus_message_close_container(reply);
        if (r < 0) {
                return r;
        }

        return 0;
}


static void manager_method_list_units_done(ListUnitsRequest *req) {
        /* All sub_req-requests are done, collect results and free when done */
        _cleanup_list_unit_request_ ListUnitsRequest *free_me = req;

        _cleanup_sd_bus_message_ sd_bus_message *reply = NULL;
        int r = sd_bus_message_new_method_return(req->request_message, &reply);
        if (r >= 0) {
                r = manager_method_list_units_encode_reply(req, reply);
        }
        if (r < 0) {
                sd_bus_reply_method_errorf(req->request_message, SD_BUS_ERROR_FAILED, "Internal error");
                return;
        }

        r = sd_bus_message_send(reply);
        if (r < 0) {
                fprintf(stderr, "Failed to send reply: %s\n", strerror(-r));
                return;
        }
}

static void manager_method_list_units_maybe_done(ListUnitsRequest *req) {
        if (req->n_done == req->n_sub_req) {
                manager_method_list_units_done(req);
        }
}


static int manager_list_units_callback(
                AgentRequest *agent_req, UNUSED sd_bus_message *m, UNUSED sd_bus_error *ret_error) {
        ListUnitsRequest *req = agent_req->userdata;
        int i = 0;

        for (int i = 0; i < req->n_sub_req; i++) {
                if (req->sub_req[i].agent_req == agent_req) {
                        break;
                }
        }

        assert(i != req->n_sub_req); /* we should have found the sub_req request */

        req->sub_req[i].m = sd_bus_message_ref(m);
        req->n_done++;

        manager_method_list_units_maybe_done(req);

        return 0;
}

static int manager_method_list_units(sd_bus_message *m, void *userdata, UNUSED sd_bus_error *ret_error) {
        Manager *manager = userdata;
        ListUnitsRequest *req = NULL;
        Node *node = NULL;

        req = malloc0_array(sizeof(*req), sizeof(req->sub_req[0]), manager->n_nodes);
        if (req == NULL) {
                return sd_bus_reply_method_errorf(m, SD_BUS_ERROR_FAILED, "Internal error");
        }
        req->request_message = sd_bus_message_ref(m);

        int i = 0;
        LIST_FOREACH(nodes, node, manager->nodes) {
                _cleanup_agent_request_ AgentRequest *agent_req = node_request_list_units(
                                node, manager_list_units_callback, req, NULL);
                if (agent_req) {
                        req->sub_req[i].agent_req = steal_pointer(&agent_req);
                        req->sub_req[i].node = node_ref(node);
                        req->n_sub_req++;
                        i++;
                }
        }

        manager_method_list_units_maybe_done(req);

        return 1;
}

static const sd_bus_vtable manager_vtable[] = {
        SD_BUS_VTABLE_START(0),
        SD_BUS_METHOD("Ping", "s", "s", manager_method_ping, 0),
        SD_BUS_METHOD("ListUnits", "", "a(sssssssouso)", manager_method_list_units, 0),
        SD_BUS_VTABLE_END
};

static int debug_messages_handler(sd_bus_message *m, UNUSED void *userdata, UNUSED sd_bus_error *ret_error) {
        fprintf(stderr,
                "Incomming public message: path: %s, iface: %s, member: %s, signature: '%s'\n",
                sd_bus_message_get_path(m),
                sd_bus_message_get_interface(m),
                sd_bus_message_get_member(m),
                sd_bus_message_get_signature(m, true));
        return 0;
}

bool manager_start(Manager *manager) {
        fprintf(stdout, "Starting Manager...\n");

        if (manager == NULL) {
                return false;
        }

        manager->user_dbus = user_bus_open(manager->event);
        if (manager->user_dbus == NULL) {
                fprintf(stderr, "Failed to open user dbus\n");
                return false;
        }

        /* Export all known nodes */
        Node *node = NULL;
        LIST_FOREACH(nodes, node, manager->nodes) {
                if (!node_export(node)) {
                        return false;
                }
        }

        int r = sd_bus_request_name(
                        manager->user_dbus, manager->user_bus_service_name, SD_BUS_NAME_REPLACE_EXISTING);
        if (r < 0) {
                fprintf(stderr, "Failed to acquire service name on user dbus: %s\n", strerror(-r));
                return false;
        }

        if (DEBUG_MESSAGES) {
                sd_bus_add_filter(manager->user_dbus, NULL, debug_messages_handler, NULL);
        }

        r = sd_bus_add_object_vtable(
                        manager->user_dbus,
                        &manager->manager_slot,
                        HIRTE_MANAGER_OBJECT_PATH,
                        MANAGER_INTERFACE,
                        manager_vtable,
                        manager);
        if (r < 0) {
                fprintf(stderr, "Failed to add node vtable: %s\n", strerror(-r));
                return false;
        }

        if (!manager_setup_node_connection_handler(manager)) {
                return false;
        }

        r = shutdown_service_register(manager->user_dbus, manager->event);
        if (r < 0) {
                fprintf(stderr, "Failed to register shutdown service\n");
                return false;
        }

        r = event_loop_add_shutdown_signals(manager->event);
        if (r < 0) {
                fprintf(stderr, "Failed to add signals to manager event loop\n");
                return false;
        }

        r = sd_event_loop(manager->event);
        if (r < 0) {
                fprintf(stderr, "Starting event loop failed: %s\n", strerror(-r));
                return false;
        }

        return true;
}

bool manager_stop(UNUSED Manager *manager) {
        fprintf(stdout, "Stopping Manager...\n");

        if (manager == NULL) {
                return false;
        }

        return true;
}