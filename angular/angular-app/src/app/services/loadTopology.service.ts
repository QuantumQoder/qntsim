import { updateTopology } from "./../store/minimal.actions";
import { Injectable } from "@angular/core";
import * as go from "gojs";
import { Observable, Subject } from "rxjs";

@Injectable({ providedIn: "root" })
export class TopologyLoaderService {
  constructor() {}
  topology: Subject<any> = new Subject<any>();
  updateTopology(data: any) {
    this.topology.next(data);
  }
  getTopology(): Observable<any> {
    return this.topology.asObservable();
  }

  loadTopologyMinimal(type, level) {
    if (type === "star") {
      //   console.log("starTopology:", this.getStarTopology(level));
      return this.getStarTopology(level);
    } else if (type === "mesh") {
      //   console.log("meshTopology:", this.getMeshTopology(level));
      return this.getMeshTopology(level);
    }
  }

  starTopology = {
    0: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
      ],
    },
    2: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "orange",
        },
        {
          key: "node3",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
        {
          from: "node2",
          to: "node3",
        },
      ],
    },
    3: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "orange",
        },
        {
          key: "node3",
          color: "lightblue",
        },
        {
          key: "node4",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
        {
          from: "node2",
          to: "node3",
        },
        {
          from: "node2",
          to: "node4",
        },
      ],
    },
    4: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "orange",
        },
        {
          key: "node3",
          color: "lightblue",
        },
        {
          key: "node4",
          color: "lightblue",
        },
        {
          key: "node5",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
        {
          from: "node2",
          to: "node3",
        },
        {
          from: "node2",
          to: "node4",
        },
        {
          from: "node2",
          to: "node5",
        },
      ],
    },
    5: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "orange",
        },
        {
          key: "node3",
          color: "lightblue",
        },
        {
          key: "node4",
          color: "lightblue",
        },
        {
          key: "node5",
          color: "lightblue",
        },
        {
          key: "node6",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
        {
          from: "node2",
          to: "node3",
        },
        {
          from: "node2",
          to: "node4",
        },
        {
          from: "node2",
          to: "node5",
        },
        {
          from: "node2",
          to: "node6",
        },
      ],
    },
  };
  meshTopology = {
    0: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
      ],
    },
    1: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "orange",
        },
        {
          key: "node3",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
        {
          from: "node2",
          to: "node3",
        },
      ],
    },
    2: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "orange",
        },
        {
          key: "node3",
          color: "orange",
        },
        {
          key: "node4",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
        {
          from: "node2",
          to: "node3",
        },
        {
          from: "node3",
          to: "node4",
        },
      ],
    },
    3: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
        },
        {
          key: "node2",
          color: "orange",
        },
        {
          key: "node3",
          color: "orange",
        },
        {
          key: "node4",
          color: "orange",
        },
        {
          key: "node5",
          color: "lightblue",
        },
        {
          key: "node6",
          color: "lightblue",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node2",
        },
        {
          from: "node2",
          to: "node3",
        },
        {
          from: "node3",
          to: "node4",
        },
        {
          from: "node4",
          to: "node2",
        },
        {
          from: "node5",
          to: "node4",
        },
        {
          from: "node6",
          to: "node3",
        },
      ],
    },
    4: {
      nodes: [
        {
          key: "node1",
          color: "lightblue",
          loc: "0 0",
        },
        {
          key: "node2",
          color: "lightblue",
          loc: "100 0",
        },
        {
          key: "node3",
          color: "orange",
          loc: "0 100",
        },
        {
          key: "node4",
          color: "orange",
          loc: "100 100",
        },
        {
          key: "node5",
          color: "orange",
          loc: "0 200",
        },
        {
          key: "node6",
          color: "orange",
          loc: "100 200",
        },
        {
          key: "node7",
          color: "lightblue",
          loc: "0 300",
        },
        {
          key: "node8",
          color: "lightblue",
          loc: "100 300",
        },
      ],
      links: [
        {
          from: "node1",
          to: "node3",
        },
        {
          from: "node2",
          to: "node4",
        },
        {
          from: "node3",
          to: "node4",
        },
        {
          from: "node4",
          to: "node5",
        },
        {
          from: "node5",
          to: "node6",
        },
        {
          from: "node6",
          to: "node4",
        },
        {
          from: "node6",
          to: "node3",
        },
        {
          from: "node3",
          to: "node5",
        },
        {
          from: "node6",
          to: "node8",
        },
        {
          from: "node5",
          to: "node7",
        },
      ],
    },
  };
  getStarTopology = (level) => {
    console.log("starTopology:", this.starTopology);
    return this.starTopology[level];
  };

  getMeshTopology = (level) => {
    console.log("meshTopology:", this.meshTopology);
    return this.meshTopology[level];
  };

  buildMinimalTopology(myDiagram, topologyType, level, showProperties) {
    var $ = go.GraphObject.make; // for conciseness in defining templates
    myDiagram = $(
      go.Diagram,
      "topology", // create a Diagram for the DIV HTML element
      {
        initialContentAlignment: go.Spot.Center, // center the content
        "undoManager.isEnabled": true, // enable undo & redo
        "panningTool.isEnabled": false,
        "toolManager.hoverDelay": 0,
        // "ViewportBoundsChanged": function (e: any) {
        //   e.diagram.toolManager.panningTool.isEnabled =
        //     !e.diagram.viewportBounds.containsRect(e.diagram.documentBounds);
        // },
      }
    );
    // define a simple Node template
    var tooltipTemplate = $(
      go.Adornment,
      "Auto",
      $(go.Shape, "RoundedRectangle", { fill: "lightyellow" }),
      $(go.TextBlock, { margin: 4 }, new go.Binding("text", "description"))
    );
    myDiagram.nodeTemplate = $(
      go.Node,
      "Auto", // the Shape will go around the TextBlockcontextMenu:
      {
        // Add the tooltip to the node
        toolTip: tooltipTemplate,
        contextMenu: $(
          go.Adornment,
          "Vertical", // that has one button
          $("ContextMenuButton", $(go.TextBlock, "Set as Sender"), {
            click: (e: go.InputEvent, obj: go.GraphObject) => {
              showProperties(e, obj, "sender");
            },
          }),
          $("ContextMenuButton", $(go.TextBlock, "Set as Receiver"), {
            click: (e: go.InputEvent, obj: go.GraphObject) => {
              showProperties(e, obj, "receiver");
            },
          })
          // more ContextMenuButtons would go here
        ),
        // contextMenu: new go.Binding("contextMenu", "", this.nodeContextMenu).ofObject(),
      },
      $(
        go.Shape,
        "RoundedRectangle",
        { strokeWidth: 0 },
        // Shape.fill is bound to Node.data.color
        new go.Binding("fill", "color")
      ),
      new go.Binding("position", "loc", go.Point.parse).makeTwoWay(
        go.Point.stringify
      ),
      $(
        go.TextBlock,
        { margin: 8 }, // some room around the text
        // TextBlock.text is bound to Node.data.key
        new go.Binding("text", "key")
      )
    );

    // function getAppropriateContextMenu(appId: any) {
    //   var $ = go.GraphObject.make;
    //   if (appId == "" || appId == undefined || appId == null) {
    //     return "";
    //   }
    //   if (appId == 4) {
    //     return $(
    //       go.Adornment,
    //       "Vertical",
    //       $("ContextMenuButton", $(go.TextBlock, "Set as endnode1"), {
    //         click: function (e: any, obj: any) {
    //           alert("Set as endnode1");
    //         },
    //       }),
    //       $("ContextMenuButton", $(go.TextBlock, "Set as endnode2"), {
    //         click: function (e: any, obj: any) {
    //           alert("Set as endnode2");
    //         },
    //       }),
    //       $("ContextMenuButton", $(go.TextBlock, "Set as endnode3"), {
    //         click: function (e: any, obj: any) {
    //           alert("Set as endnode3");
    //         },
    //       }),
    //       $("ContextMenuButton", $(go.TextBlock, "Set as endnode4"), {
    //         click: function (e: any, obj: any) {
    //           alert("Set as endnode4");
    //         },
    //       })
    //     );
    //   } else {
    //     return $(
    //       go.Adornment,
    //       "Vertical",
    //       $("ContextMenuButton", $(go.TextBlock, "Set as sender"), {
    //         click: function (e: any, obj: any) {
    //           alert("Set as sender");
    //         },
    //       }),
    //       $("ContextMenuButton", $(go.TextBlock, "Set as receiver"), {
    //         click: function (e: any, obj: any) {
    //           alert("Set as receiver");
    //         },
    //       })
    //     );
    //   }
    // }

    myDiagram.linkTemplate = $(go.Link, $(go.Shape));
    console.log("topologyType", topologyType, "level", level);
    // console.log(this.loadTopologyMinimal(topologyType, level));
    const preloadedTopology = this.loadTopologyMinimal(topologyType, level);
    myDiagram.model = new go.GraphLinksModel(
      preloadedTopology.nodes,
      preloadedTopology.links
    );
    return myDiagram;
  }
  addDescriptionToNodes(topologyData, info) {
    topologyData.nodes = topologyData.nodes.map((node) => {
      node.description = node.color === "orange" ? info.service : info.end;
      return node;
    });
    console.log("topologyData", topologyData.nodes);
    return topologyData;
  }
  updateDiagram(data: any, topology) {
    topology.model = new go.GraphLinksModel(data.nodes, data.links);
    // console.log(this.topology.model.nodeDataArray);
  }

  getAppConfig(appSettingsForm: any) {
    return {
      2: {
        sender: appSettingsForm.get("sender")?.value,
        receiver: appSettingsForm.get("receiver")?.value,
        startTime: 1e12,
        size: appSettingsForm.get("size")?.value,
        priority: 0,
        targetFidelity: appSettingsForm.get("targetFidelity")?.value,
        timeout: 2e12,
      },
      1: {
        sender: appSettingsForm.get("sender")?.value,
        receiver: appSettingsForm.get("receiver")?.value,
        keyLength: String(appSettingsForm.get("keyLength")?.value),
      },
      3: {
        sender: appSettingsForm.get("sender")?.value,
        receiver: appSettingsForm.get("receiver")?.value,
        amplitude1: "0.70710678118+0j",
        amplitude2: "0-0.70710678118j",
      },
      4: {
        endnode1: appSettingsForm.get("endnode1")?.value,
        endnode2: appSettingsForm.get("endnode2")?.value,
        endnode3: appSettingsForm.get("endnode3")?.value,
        middlenode: appSettingsForm.get("middleNode")?.value,
      },
      5: {
        sender: appSettingsForm.get("sender")?.value,
        receiver: appSettingsForm.get("receiver")?.value,
        sequenceLength: 3,
        key: appSettingsForm.get("key")?.value,
      },
      6: {
        sender: appSettingsForm.get("sender")?.value,
        receiver: appSettingsForm.get("receiver")?.value,
        sequenceLength: "2",
        message: appSettingsForm.get("message")?.value,
      },
      7: {
        sender: {
          node: appSettingsForm.get("sender")?.value,
          message: appSettingsForm.get("messageIp1")?.value,
          userID: "1010",
          num_check_bits: 4,
          num_decoy_photons: 4,
        },
        receiver: {
          node: appSettingsForm.get("receiver")?.value,
          userID: "1011",
        },
        bell_type: "10",
        attack: "none",
      },
      8: {
        sender: appSettingsForm.get("sender")?.value,
        receiver: appSettingsForm.get("receiver")?.value,
        message1: appSettingsForm.get("message1")?.value,
        message2: appSettingsForm.get("message2")?.value,
        num_photons: 5,
        attack: "",
      },
      9: {
        sender: {
          node: appSettingsForm.get("sender")?.value,
          message: appSettingsForm.get("message")?.value,
        },
        receiver: {
          node: appSettingsForm.get("receiver")?.value,
        },
        bell_type: "10",
        attack: "none",
      },
      10: {
        sender: {
          node: appSettingsForm.get("sender")?.value,
          message: appSettingsForm.get("inputMessage")?.value,
          userID: "1011",
          num_check_bits: 4,
          num_decoy_photons: 4,
        },
        receiver: {
          node: appSettingsForm.get("receiver")?.value,
          userID: "1010",
        },
        bell_type: "10",
        error_threshold: 0.5,
        attack: "none",
        channel: 1,
      },
    };
  }
  getTopologyRequestPayload(nodeArray, linkRequestArray, cc) {
    return {
      nodes: nodeArray,
      quantum_connections: linkRequestArray,
      classical_connections: cc,
      detector_properties: {
        efficiency: 1,
        count_rate: 25e6,
        time_resolution: 150,
      },

      light_source_properties: {
        frequency: 2000,
        wavelength: 1550,
        bandwidth: 0,
        mean_photon_num: 0.1,
        phase_error: 0,
      },
    };
  }
  getRequestPayload(appForm: any, topology, appConfig, debug) {
    return {
      application: appForm.get("app")?.value,
      topology: topology,
      appSettings: appConfig,
      debug: {
        modules: debug.modules,
        logLevel: debug.loggingLevel.value,
      },
    };
  }
  setAlert(appSettingsForm, app_id) {
    if (app_id == 5) {
      if (appSettingsForm.get("key")?.value.length % 2 != 0) {
        alert("Key length should be even");
        // this.spinner = false
        return;
      }
    }
    if (app_id == 10) {
      if (appSettingsForm.get("inputMessage")?.value.length % 2 != 0) {
        alert("Message length should be even ");
        // this.spinner = false
        return;
      }
    }
    if (app_id == 6) {
      if (appSettingsForm.get("message")?.value.length % 2 != 0) {
        alert("Message length should be even ");
        // this.spinner = false
        return;
      }
    }
    if (app_id == 7) {
      if (appSettingsForm.get("messageIp1")?.value.length % 2 != 0) {
        alert("Message length should be even ");
        // this.spinner = false
        return;
      }
    }

    if (app_id == 10) {
      if (appSettingsForm.get("inputMessage")?.value.length % 2 != 0) {
        alert("Message length should be even");
        return;
      }
    }

    if (app_id == 8) {
      if (
        appSettingsForm.get("message1")?.value.length !=
        appSettingsForm.get("message2")?.value.length
      ) {
        alert("Sender's Message and Receiver's message length should be same.");
        return;
      }
    }
    if (app_id != 4) {
      console.log(app_id);
      if (appSettingsForm.get("sender")?.value == "") {
        alert("Please select a sender");
        return;
      } else if (appSettingsForm.get("receiver")?.value == "") {
        alert("Please select a receiver.");
        return;
      }
    }
    if (app_id == 4) {
      if (
        appSettingsForm.get("endnode1")?.value == "" ||
        appSettingsForm.get("endnode2")?.value == "" ||
        appSettingsForm.get("endnode3")?.value == ""
      ) {
        alert("Please select End Nodes.");
        return;
      }
    }
  }
  setAlertAdvanced(
    app_id,
    appSettingsForm,
    nodesSelection,
    lightSourceProps,
    nodesData,
    myDiagram
  ): boolean {
    if (app_id == 5) {
      if (appSettingsForm.get("message")?.value.length % 2 != 0) {
        alert("Message length should be even ");
        // this.spinner = false
        return false;
      }
    }

    if (app_id == 10 || app_id == 9 || app_id == 7 || app_id == 6) {
      if (nodesSelection.message == "") {
        alert("Please select a message");
        return false;
      }
      if (nodesSelection.message.length % 2 != 0) {
        alert("Message length should be even ");
        return false;
      }
    }
    if (app_id == 8) {
      if (appSettingsForm.get("message1")?.value.length % 2 != 0) {
        alert("Message1 length should be even ");
        // this.spinner = false
        return false;
      }
      if (appSettingsForm.get("message2")?.value.length % 2 != 0) {
        alert("Message2 length should be even ");
        // this.spinner = false
        return false;
      }
    }
    if (app_id != 4) {
      if (nodesSelection.sender == "") {
        alert("Please select a sender");
        return false;
      } else if (nodesSelection.receiver == "") {
        alert("Please select a receiver.");
        return false;
      } else if (nodesSelection.sender == nodesSelection.receiver) {
        alert("Sender and Receiver cannot be same node");
        return false;
      }
    }
    if (app_id == 10) {
      if (
        lightSourceProps.meanPhotonNum >= 0 &&
        !(lightSourceProps.meanPhotonNum <= 1)
      ) {
        alert("Mean Photon Number should be between 0 and 1");
        return false;
      }
    }
    if (app_id == 4) {
      let middleNode = appSettingsForm.get("middleNode")?.value;
      //nodesSelection.endNode1)
      //nodesSelection.endNode2)
      //nodesSelection.endNode3)
      if (
        nodesSelection.endNode1 == "" ||
        nodesSelection.endNode2 == "" ||
        nodesSelection.endNode3 == "" ||
        middleNode == ""
      ) {
        alert("Please select End Nodes.");
        return false;
      }
      if (
        nodesSelection.endNode1 == nodesSelection.endNode2 ||
        nodesSelection.endNode2 == nodesSelection.endNode3 ||
        nodesSelection.endNode3 == nodesSelection.endNode1
      ) {
        alert("End Nodes cannot be same node");
        return false;
      }
    }
    for (let i = 0; i < myDiagram.nodeDataArray.length; i++) {
      if (!((myDiagram.nodeDataArray[i] as any).key in nodesData)) {
        alert(
          "Please configure the node named:" +
            (myDiagram.nodeDataArray[i] as any).text
        );
        return false;
      }
    }
    return true;
  }
}
