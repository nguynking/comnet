"""
Your awesome Distance Vector router for CS 168

Based on skeleton code by:
  MurphyMc, zhangwen0411, lab352
"""

import sim.api as api
from cs168.dv import (
    RoutePacket,
    Table,
    TableEntry,
    DVRouterBase,
    Ports,
    FOREVER,
    INFINITY,
)


class DVRouter(DVRouterBase):

    # A route should time out after this interval
    ROUTE_TTL = 15

    # -----------------------------------------------
    # At most one of these should ever be on at once
    SPLIT_HORIZON = False
    POISON_REVERSE = False
    # -----------------------------------------------

    # Determines if you send poison for expired routes
    POISON_EXPIRED = False

    # Determines if you send updates when a link comes up
    SEND_ON_LINK_UP = False

    # Determines if you send poison when a link goes down
    POISON_ON_LINK_DOWN = False

    def __init__(self):
        """
        Called when the instance is initialized.
        DO NOT remove any existing code from this method.
        However, feel free to add to it for memory purposes in the final stage!
        """
        assert not (
            self.SPLIT_HORIZON and self.POISON_REVERSE
        ), "Split horizon and poison reverse can't both be on"

        self.start_timer()  # Starts signaling the timer at correct rate.

        # Contains all current ports and their latencies.
        # See the write-up for documentation.
        self.ports = Ports()

        # This is the table that contains all current routes
        self.table = Table()
        self.table.owner = self

        # Record the latest route advertisement sent out of each port for each destination
        self.history = {}

    def add_static_route(self, host, port):
        """
        Adds a static route to this router's table.

        Called automatically by the framework whenever a host is connected
        to this router.

        :param host: the host.
        :param port: the port that the host is attached to.
        :returns: nothing.
        """
        # `port` should have been added to `peer_tables` by `handle_link_up`
        # when the link came up.
        assert port in self.ports.get_all_ports(), "Link should be up, but is not."

        # TODO: fill this in!
        self.table[host] = TableEntry(
            dst=host,
            port=port,
            latency=self.ports.get_latency(port),
            expire_time=FOREVER
        )

    def handle_data_packet(self, packet, in_port):
        """
        Called when a data packet arrives at this router.

        You may want to forward the packet, drop the packet, etc. here.

        :param packet: the packet that arrived.
        :param in_port: the port from which the packet arrived.
        :return: nothing.
        """
        # TODO: fill this in!
        # this packet has the destination (dst) and source (src)
        if packet.dst not in self.table.keys():
            return

        entry = self.table[packet.dst]
        if entry.latency >= INFINITY:
            return

        self.send(packet=packet, port=entry.port)

    def send_routes(self, force=False, single_port=None):
        """
        Send route advertisements for all routes in the table.

        :param force: if True, advertises ALL routes in the table;
                      otherwise, advertises only those routes that have
                      changed since the last advertisement.
               single_port: if not None, sends updates only to that port; to
                            be used in conjunction with handle_link_up.
        :return: nothing.
        """
        # TODO: fill this in!
        ports_to_update = [single_port] if single_port is not None else self.ports.get_all_ports()
        for host, entry in self.table.items():
            for port in ports_to_update:
                exist_in_history = (host, port) in self.history.keys()

                if exist_in_history:
                    old_ad = self.history[(host, port)]

                # split horizon
                if self.SPLIT_HORIZON:
                    # different port: advertise the route
                    if port != entry.port:
                        # force = False
                        if not force:
                            if not exist_in_history or old_ad.destination != host or old_ad.latency != entry.latency:
                                self.send_route(port, entry.dst, entry.latency)
                                self.history[(host, port)] = RoutePacket(entry.dst, entry.latency)

                        # force = True
                        else:
                            self.send_route(port, entry.dst, entry.latency)
                            self.history[(host, port)] = RoutePacket(entry.dst, entry.latency)

                # poison reverse
                elif self.POISON_REVERSE:
                    # same port: advertise the route with latency = INFINITY
                    if port == entry.port:
                        # force = False
                        if not force:
                            if not exist_in_history or old_ad.destination != host or old_ad.latency != INFINITY:
                                self.send_route(port, entry.dst, INFINITY)
                                self.history[(host, port)] = RoutePacket(entry.dst, INFINITY)

                        # force = True
                        else:
                            self.send_route(port, entry.dst, INFINITY)
                            self.history[(host, port)] = RoutePacket(entry.dst, INFINITY)

                    # different port: advertise the route
                    else:
                        # force = False
                        if not force:
                            if not exist_in_history or old_ad.destination != host or old_ad.latency != entry.latency:
                                self.send_route(port, entry.dst, entry.latency)
                                self.history[(host, port)] = RoutePacket(entry.dst, entry.latency)

                        # force = True
                        else:
                            self.send_route(port, entry.dst, entry.latency)
                            self.history[(host, port)] = RoutePacket(entry.dst, entry.latency)

                # just advertise the route
                else:
                    self.send_route(port, entry.dst, entry.latency)
                    self.history[(host, port)] = RoutePacket(entry.dst, entry.latency)

    def expire_routes(self):
        """
        Clears out expired routes from table.
        accordingly.
        """
        # TODO: fill this in!
        # dictionary changes size during iteration
        hosts = list(self.table.keys())
        for host in hosts:
            route = self.table[host]
            if self.POISON_EXPIRED and api.current_time() > route.expire_time:
                self.table[host] = TableEntry(
                    dst=host,
                    port=route.port,
                    latency=INFINITY,
                    expire_time=self.ROUTE_TTL
                )
            elif api.current_time() > route.expire_time:
                self.s_log(f"{route} has expired.")
                del self.table[host]

    def handle_route_advertisement(self, route_dst, route_latency, port):
        """
        Called when the router receives a route advertisement from a neighbor.

        :param route_dst: the destination of the advertised route.
        :param route_latency: latency from the neighbor to the destination.
        :param port: the port that the advertisement arrived on.
        :return: nothing.
        """
        # TODO: fill this in!
        new_latency = route_latency + self.ports.get_latency(port)
        current_route = self.table.get(route_dst)
        new_route = TableEntry(
            dst=route_dst,
            port=port,
            latency=new_latency,
            expire_time=api.current_time() + self.ROUTE_TTL
        )

        if not current_route:
            self.table[route_dst] = new_route
            self.send_routes(force=False)

        elif new_latency < current_route.latency:
            self.table[route_dst] = new_route
            self.send_routes(force=False)
        
        elif port == current_route.port and route_latency >= INFINITY:
            self.table[route_dst] = TableEntry(
                dst=route_dst,
                port=port,
                latency=INFINITY,
                expire_time=current_route.expire_time
            ) 
            self.send_routes(force=False)

        elif current_route.port == port:
            self.table[route_dst] = new_route
            self.send_routes(force=False)


    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this router goes up.

        :param port: the port that the link is attached to.
        :param latency: the link latency.
        :returns: nothing.
        """
        self.ports.add_port(port, latency)

        # TODO: fill in the rest!
        if self.SEND_ON_LINK_UP:
            self.send_routes(force=False, single_port=port)

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this router goes down.

        :param port: the port number used by the link.
        :returns: nothing.
        """
        self.ports.remove_port(port)

        # TODO: fill this in!
        for host in list(self.table.keys()):
            if self.table[host].port == port:
                if self.POISON_ON_LINK_DOWN:
                    # poison and immediately send any routes that need to be updated
                    poison_route = TableEntry(host, port, latency=INFINITY, expire_time=self.table[host].expire_time)
                    self.table[host] = poison_route
                    self.send_routes(force=False)

                    # remove any routes that go through that link
        # for host in list(self.table.keys()):
        #     if self.table[host].port == port:
        #         del self.table[host]

    # Feel free to add any helper methods!
