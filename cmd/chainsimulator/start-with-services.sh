#!/bin/bash

# TODO: refactor sed usages by using overridable configs when the rc/v1.7.next1 is released

if [[ -z "${EVENTS_NOTIFIER_URL}" ]]; then
  echo "not activating events notifier in external.toml"
else
  echo "

[[HostDriversConfig]]
    # This flag shall only be used for observer nodes
    Enabled = true

    # This flag will start the WebSocket connector as server or client (can be \"client\" or \"server\")
    Mode = \"client\"

    # URL for the WebSocket client/server connection
    # This value represents the IP address and port number that the WebSocket client or server will use to establish a connection.
    URL = \"$EVENTS_NOTIFIER_URL\"

    # After a message will be sent it will wait for an ack message if this flag is enabled
    WithAcknowledge = true

    # The duration in seconds to wait for an acknowledgment message, after this time passes an error will be returned
    AcknowledgeTimeoutInSec = 60

    # This flag defines the marshaller type. Currently supported: \"json\", \"gogo protobuf\"
    MarshallerType = \"gogo protobuf\"

    # The number of seconds when the client will try again to send the data
    RetryDurationInSec = 5

    # Sets if, in case of data payload processing error, we should block or not the advancement to the next processing event. Set this to true if you wish the node to stop processing blocks if the client/server encounters errors while processing requests.
    BlockingAckOnError = true

    # Set to true to drop messages if there is no active WebSocket connection to send to.
    DropMessagesIfNoConnection = false

    # Defines the payload version. Version will be changed when there are breaking
    # changes on payload data. The receiver/consumer will have to know how to handle different
    # versions. The version will be sent as metadata in the websocket message.
    Version = 1
" >> ./config/node/config/external.toml

  echo "activated events notifier in external.toml"
fi

if [[ -z "${ELASTIC_SEARCH_URL}" ]]; then
  echo "not activating elastic search in external.toml"
else
  sed -i '/Strongly suggested to activate this on a regular observer node./{n;s/Enabled           = false/Enabled           = true/}' ./config/node/config/external.toml

  echo "activated elastic search in external.toml"
fi

./chainsimulator $@