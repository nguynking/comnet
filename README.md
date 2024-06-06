# comnet

**Status: In Progress**

These are my solutions to [CS 168 - Introduction to the Internet: Architecture and Protocols](https://cs168.io/) projects at Berkeley taught by [Sylvia Ratnasamy](https://people.eecs.berkeley.edu/~sylvia/) & [Rob Shakir](https://rob.sh/).

All projects are written in Python. I'm not taking the class, so this is just for fun. This class doesn't have recordings but its materials are enough to understand most of the concepts.

**Textbook:** Computer Networking: A Top-Down Approach, 7th Edition

> [!NOTE]
> I will write detailed notes for each lecture after completing all 3 projects.

## Project 1: Distance Vector Routing

The goal of this project is for you to learn to implement distributed algorithms for intradomain routing,
where all routers run an algorithm that allows them to transport packets to their destination, but no central
authority determines the forwarding paths. You will implement code to run at a router, and we will provide
a routing simulator that builds a graph connecting your routers to each other and to simulated hosts on
the network. By the end of this project, you will have implemented a version of a distance vector protocol
that computes efficient paths across the network.

## Project 2: Traceroute

Your goal is to implement traceroute in Python. You will do this by implementing the various TODO's in `traceroute.py`.

The project is designed to run correctly against the internet in addition to the autograder. You are encouraged to try this out, both for debugging purposes, and for fun.

This project does not require a great deal of code to complete. Instead, the project is largely designed to test your ability to independently research and apply the necessary information given a certain degree of ambiguity. As a result, you are highly encouraged to carefully read the spec and starter code before you begin working. While it may feel slow, we can assure you that doing so will ultimately save you a great deal of time.

## Project 3: Transport

The goal of this project is to implement a Socket that implements a TCP protocol similar to those you
can find in the Internet. A socket is an abstraction between the application layer and the transport layer
that allows an application to easily use the underlying transport protocol (TCP in this case). While sockets
are usually implemented by the operating system, your socket will be a user space implementation written
in Python. We will provide a network simulator and a Python TCP/IP stack, minus parts that you must
implement (which is the core of the actual TCP protocol). In this project, you won’t be implementing
applications that use this Socket. Instead, you will be implementing core parts of the protocol, and the
tests we provide will act as applications. These applications will use the Socket class you write and expect
the behavior defined in this specification.
