import { updateTopology } from "./../../store/minimal.actions";
import { HoldingDataService } from "src/app/services/holding-data.service";
import { CookieService } from "ngx-cookie-service";
import { ApiServiceService } from "../../services/api-service.service";
import {
  AfterViewInit,
  Component,
  OnDestroy,
  OnInit,
  ViewEncapsulation,
} from "@angular/core";
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
} from "@angular/forms";
import * as go from "gojs";
import { Observable, map } from "rxjs";
import { ConditionsService } from "src/app/services/conditions.service";
import { Router } from "@angular/router";
import { environment } from "src/environments/environment";
import { DiagramStorageService } from "src/app/services/diagram-storage.service";
import { Store } from "@ngrx/store";
import { TopologyLoaderService } from "src/app/services/loadTopology.service";

@Component({
  selector: "app-minimal",
  templateUrl: "./minimal.component.html",
  styleUrls: ["./minimal.component.less"],
  encapsulation: ViewEncapsulation.Emulated,
})
export class MinimalComponent implements OnInit, AfterViewInit, OnDestroy {
  stateStoreValue: Observable<any>;
  type = "Star";
  data: string = "|1\\rangle";
  debug = {
    loggingLevel: {
      name: "INFO",
      value: "info",
    },
    modules: [],
  };
  debugOptions = {
    moduleOptions: [],
    loggingLevelOptions: [],
  };

  radio = {
    1: true,
    2: false,
    3: false,
    4: false,
  };
  amplitude: any;
  e2e = {
    targetFidelity: 0.5,
    size: 6,
  };
  senderNodes: any[] = [];
  receiverNodes: any[] = [];
  serviceNodes: any[] = [];
  endNodes: any[] = [];
  topology: any;
  topologyData: any;
  request: Request;
  spinner: boolean = false;
  topologyForm: any;
  appForm;
  applist: any;
  nodes: any;
  distance: number = 100;
  appSettingsForm: any;
  typeOptions = ["Star", "Mesh"];
  level: number = 2;
  cc: any[] = [];
  appSettingsResult: any;
  appConfig: any;
  info = {
    end: "Origin or destination nodes for user/application requests, each connected to one service node.",
    service:
      "Entanglement-swapping nodes (similar to classical routers) connect non-neighbor nodes\n but don't support request creation or application hosting.",
  };
  lastValue = {
    type: this.type,
    level: this.level,
  };
  endNode1: any[] = ["node1"];
  endNode2: any[] = ["node3"];
  app_data: {
    1: string;
    2: string;
    3: string;
    4: string;
    5: string;
    6: string;
    7: string;
    8: string;
    9: string;
    10: string;
  };
  valid: any;
  nodeTemplateCopy: any;
  contextMenuVersion1: any;
  contextMenuVersion2: any;
  subscription: any;
  endNode3: any[] = ["node4"];

  constructor(
    private fb: FormBuilder,
    private service: ConditionsService,
    private route: Router,
    private holdingData: HoldingDataService,
    private api: ApiServiceService,
    private diagramStorage: DiagramStorageService,
    private store: Store<{ minimal: any }>,
    private topologyLoader: TopologyLoaderService
  ) {
    this.stateStoreValue = store.select("minimal");
    this.stateStoreValue.subscribe((data) => {
      console.log(data);
    });
  }
  ngOnDestroy(): void {
    this.diagramStorage.updateMinimalFormData({
      appForm: this.appForm,
      appSettingsForm: this.appSettingsForm,
    });
    this.subscription.unsubscribe();
  }
  ngAfterViewInit(): void {
    let diagramData = this.diagramStorage.getMinimalValues();
    this.subscription = this.diagramStorage.currentMinimalFormData.subscribe(
      (formData) => {
        if (formData) {
          this.appForm = formData.appForm;
          this.appSettingsForm = formData.appSettingsForm;
        }
      }
    );
    if (diagramData) {
      this.level = diagramData.level;
      this.type = diagramData.type;
    }

    this.topologyData = this.topologyLoader.loadTopologyMinimal(
      this.type.toLowerCase(),
      this.level
    );
    this.init(this.topologyData.nodes, this.topologyData.links);
    this.updateNodes();
  }
  toggle(data: any) {
    var content;
    var toggler;
    if (data == 1) {
      content = document.getElementById("content1") as any;
      toggler = document.getElementById("toggle-button1") as any;
      toggler.classList.toggle("active");

      if (toggler.classList.contains("active")) {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    } else if (data == 2) {
      content = document.getElementById("content2") as any;
      toggler = document.getElementById("toggle-button2") as any;
      toggler.classList.toggle("active");
      // content.classList.toggle('active');
      if (toggler.classList.contains("active")) {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    }
  }
  routeTo(url: string) {
    this.holdingData.setRoute("minimal");
    this.route.navigate([`/${url}`]);
  }
  setSettings(formData: any) {
    let form = {};
    this.appSettingsForm = null;
    for (let i = 0; i < formData.length; i++) {
      form[formData[i].formField] = new FormControl("");
    }
    this.appSettingsForm.addControl(form);
  }
  ngOnInit(): void {
    this.topologyForm = this.fb.group({
      type: ["Star", Validators.required],
      level: [2, Validators.required],
      noOfMemories: [500, Validators.required],
      distance: [100, [Validators.required]],
      attenuity: [0.0001, Validators.required],
    });
    this.appForm = this.fb.group({
      app: ["", Validators.required],
    });
    this.appSettingsForm = this.fb.group({
      sender: ["", Validators.required],
      receiver: ["", Validators.required],
      targetFidelity: [0.5],
      size: [6],
      // 'amplitude': ['', Validators.required],
    });
    this.debugOptions.moduleOptions = [
      {
        name: "NETWORK",
        value: "network",
      },
      {
        name: "PHYSICAL",
        value: "physical",
      },
      {
        name: "LINK",
        value: "link",
      },
      {
        name: "TRANSPORT",
        value: "transport",
      },

      {
        name: "APPLICATION",
        value: "application",
      },
      {
        name: "EVENT SIMULATION",
        value: "eventSimulation",
      },
    ];
    this.debugOptions.loggingLevelOptions = [
      {
        name: "DEBUG",
        value: "debug",
      },
      {
        name: "INFO",
        value: "info",
      },
    ];
    // this.appSettingsForm
    this.app_data = this.holdingData.getAppData();
    this.service
      .getAppList()
      .pipe(map((d: any) => d.appList))
      .subscribe((result: any) => (this.applist = result));
    var data = this.api.getCredentials();
    this.api.accessToken(data).subscribe((result: any) => {
      localStorage.setItem("access", result.access);
    });
    this.getAppSettingsResults();
  }
  updateDiagram(data: any) {
    this.topology.model = new go.GraphLinksModel(data.nodes, data.links);
    console.log(this.topology.model.nodeDataArray);
  }
  allowBitsInput($event: any) {
    if ($event.key.match(/[0-1]*/)["0"]) {
    } else {
      $event.preventDefault();
    }
  }
  updateDistance() {
    this.distance = this.topologyForm.get("distance")?.value;
  }
  updateNodes() {
    this.serviceNodes = this.topologyData.nodes.filter(
      (node) => node.color === "orange"
    );
    this.endNodes = this.topologyData.nodes.filter(
      (node) => node.color === "lightblue"
    );

    if (this.endNodes.length) {
      this.senderNodes = this.endNodes;
      this.receiverNodes = this.endNodes;
      this.endNode1 = this.endNodes;
      this.endNode2 = this.endNodes;
      this.endNode3 = this.endNodes;
    }
  }

  endNode(data: any) {
    // var remainingNodes = [];
    console.log(data);
    this.endNode1 = this.endNodes;
    this.endNode1 = this.endNode1.filter((e) => e.key != data);
    console.log(this.endNode1);
  }

  init(nodes: any, links: any) {
    var $ = go.GraphObject.make; // for conciseness in defining templates
    this.topology = $(
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
    this.topology.nodeTemplate = $(
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
              this.showProperties(e, obj, "sender");
            },
          }),
          $("ContextMenuButton", $(go.TextBlock, "Set as Receiver"), {
            click: (e: go.InputEvent, obj: go.GraphObject) => {
              this.showProperties(e, obj, "receiver");
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

    this.topology.linkTemplate = $(go.Link, $(go.Shape));
    this.topology.model = new go.GraphLinksModel(nodes, links);
    this.topology.addDiagramListener("Modified", () => {
      this.diagramStorage.setMinimalValues({
        topology: this.topology.model,
        type: this.type,
        level: this.level,
      });
      // console.log(this.diagramStorage.getAdvancedDiagramModel())
    });
  }

  getAppropriateContextMenu(appId: any) {
    var $ = go.GraphObject.make;
    if (appId == "" || appId == undefined || appId == null) {
      return "";
    }
    if (appId == 4) {
      return $(
        go.Adornment,
        "Vertical",
        $("ContextMenuButton", $(go.TextBlock, "Set as endnode1"), {
          click: function (e: any, obj: any) {
            alert("Set as endnode1");
          },
        }),
        $("ContextMenuButton", $(go.TextBlock, "Set as endnode2"), {
          click: function (e: any, obj: any) {
            alert("Set as endnode2");
          },
        }),
        $("ContextMenuButton", $(go.TextBlock, "Set as endnode3"), {
          click: function (e: any, obj: any) {
            alert("Set as endnode3");
          },
        }),
        $("ContextMenuButton", $(go.TextBlock, "Set as endnode4"), {
          click: function (e: any, obj: any) {
            alert("Set as endnode4");
          },
        })
      );
    } else {
      return $(
        go.Adornment,
        "Vertical",
        $("ContextMenuButton", $(go.TextBlock, "Set as sender"), {
          click: function (e: any, obj: any) {
            alert("Set as sender");
          },
        }),
        $("ContextMenuButton", $(go.TextBlock, "Set as receiver"), {
          click: function (e: any, obj: any) {
            alert("Set as receiver");
          },
        })
      );
    }
  }

  showProperties(e: go.InputEvent, obj: any, data: String) {
    console.log(obj);
    var node = obj.part.adornedPart.data.key;
    console.log(node);
    this.nodes = this.topologyData.nodes;
    this.appSettingsForm.get(data)?.patchValue(node);
  }

  getApp($event: any) {
    let app_id = this.appForm.get("app")?.value;
    this.nodes = this.topologyData.nodes;

    if (app_id == 4) {
      this.level = 3;
      this.topologyForm.get("level").patchValue(this.level);
      // this.levelChange();
      this.updateJson();
    }
    this.updateNodes();
    localStorage.setItem("app_id", this.appForm.get("app")?.value);
    localStorage.setItem("app", this.app_data[this.appForm.get("app")?.value]);
    this.buildForm(this.appForm.get("app")?.value);
    if (this.topologyForm.get("type")?.value == "Star") {
      this.appSettingsForm.get("endnode1").patchValue("node1");
      this.appSettingsForm.get("endnode2").patchValue("node3");
      this.appSettingsForm.get("endnode3").patchValue("node4");
    } else if (this.topologyForm.get("type")?.value == "Mesh") {
      this.appSettingsForm.get("endnode1").patchValue("node1");
      this.appSettingsForm.get("endnode2").patchValue("node5");
      this.appSettingsForm.get("endnode3").patchValue("node6");
    }
  }
  runApp() {
    // this.spinner = true;
    // var linkArray = [];
    // var nodeArray = []
    var linkRequestArray = [];
    const nodeDataArray = this.topologyData.nodes;
    const linkDataArray = this.topologyData.links;
    const app_id = this.appForm.get("app")?.value;
    this.topologyLoader.setAlert(this.appSettingsForm, app_id);
    const nodeArray = nodeDataArray.map((node: any) => ({
      Name: node.key,
      Type: node.color === "orange" ? "service" : "end",
      noOfMemory: this.topologyForm.get("noOfMemories")?.value,
      memory: this.service.getMemory(),
      swap_success_rate: 0.99,
      swap_degradation: 1,
    }));
    if (app_id != 4) {
      localStorage.setItem("sender", this.appSettingsForm.get("sender")?.value);
      localStorage.setItem(
        "receiver",
        this.appSettingsForm.get("receiver")?.value
      );
    }
    let cc = [];
    this.spinner = true;
    localStorage.setItem("app_id", app_id);
    console.log(nodeArray);
    for (const link of linkDataArray) {
      const linkData = {
        Nodes: [link.from, link.to],
        Attenuation: this.topologyForm.get("attenuity")?.value,
        Distance: this.topologyForm.get("distance")?.value,
        powerLoss: 0,
      };
      linkRequestArray.push(linkData);
    }

    this.cc = [];
    cc = nodeDataArray.flatMap((item1, index1) =>
      nodeDataArray.map((item2, index2) => [item1.key, item2.key])
    );

    this.cc = nodeDataArray.flatMap((item1) =>
      nodeDataArray.map((item2) => ({
        Nodes: [item1.key, item2.key],
        Delay: item1.key === item2.key ? 0 : 10000000000,
        Distance: item1.key === item2.key ? 0 : 1000,
      }))
    );

    var topology = this.topologyLoader.getTopologyRequestPayload(
      nodeArray,
      linkDataArray,
      this.cc
    );
    this.getAppSetting(this.appForm.get("app")?.value);
    console.log(this.appConfig);
    this.debug.modules = this.debug.modules.map((module) => module.value);

    var request = this.topologyLoader.getRequestPayload(
      this.appForm,
      topology,
      this.appConfig,
      this.debug
    );

    this.api.runApplication(request, environment.apiUrl).subscribe(
      (result) => {
        this.spinner = true;
        console.log(this.spinner);
        this.service.setResult(result);
      },
      (error) => {
        this.spinner = false;
        console.log(error);
        alert(
          "Error has occurred:" + "" + error.status + "-" + error.statusText
        );
      },
      () => {
        this.spinner = false;
        this.route.navigate(["/results"]);
      }
    );
  }
  buildForm(app: Number) {
    switch (app) {
      case 1:
        if (!this.appSettingsForm.controls["keyLength"])
          this.appSettingsForm.addControl(
            "keyLength",
            new FormControl("5", Validators.required)
          );
        break;
      case 2:
        console.log(app);
        break;
      case 3:
        console.log(app);
        break;
      case 4:
        if (!this.appSettingsForm.controls["endnode1"])
          this.appSettingsForm.addControl(
            "endnode1",
            new FormControl("node1", Validators.required)
          );
        if (!this.appSettingsForm.controls["endnode2"])
          this.appSettingsForm.addControl(
            "endnode2",
            new FormControl("node3", Validators.required)
          );
        if (!this.appSettingsForm.controls["endnode3"])
          this.appSettingsForm.addControl(
            "endnode3",
            new FormControl("node4", Validators.required)
          );
        if (!this.appSettingsForm.controls["middleNode"])
          this.appSettingsForm.addControl(
            "middleNode",
            new FormControl("node2", Validators.required)
          );
        console.log(this.appSettingsForm);
        break;
      case 5:
        if (!this.appSettingsForm.controls["key"])
          this.appSettingsForm.addControl(
            "key",
            new FormControl("10100111", [
              Validators.required,
              evenLengthValidator,
              Validators.minLength(8),
              Validators.maxLength(10),
            ])
          );
        break;
      case 6:
        if (!this.appSettingsForm.controls["message"])
          this.appSettingsForm.addControl(
            "message",
            new FormControl("10100111", [
              Validators.required,
              evenLengthValidator,
              Validators.minLength(8),
              Validators.maxLength(10),
            ])
          );
        break;
      case 7:
        if (!this.appSettingsForm.controls["messageIp1"])
          this.appSettingsForm.addControl(
            "messageIp1",
            new FormControl("10100111", [
              Validators.required,
              evenLengthValidator,
              Validators.minLength(8),
              Validators.maxLength(10),
            ])
          );
        break;
      case 8:
        if (!this.appSettingsForm.controls["message1"])
          this.appSettingsForm.addControl(
            "message1",
            new FormControl("hello", Validators.required)
          );
        if (!this.appSettingsForm.controls["message2"])
          this.appSettingsForm.addControl(
            "message2",
            new FormControl("world", Validators.required)
          );
        break;
      case 9:
        if (!this.appSettingsForm.controls["message"])
          this.appSettingsForm.addControl(
            "message",
            new FormControl("", Validators.required)
          );
        break;
      case 10:
        if (!this.appSettingsForm.controls["inputMessage"])
          this.appSettingsForm.addControl(
            "inputMessage",
            new FormControl("101110", Validators.required)
          );
        break;
    }
    console.log(this.appSettingsForm);
  }

  getAppSettingsResults() {
    this.service.getAppSetting().subscribe((results: any) => {
      this.appSettingsResult = results;
    });
  }
  getAppSetting(app_id: any) {
    const appConfigMap = this.topologyLoader.getAppConfig(this.appSettingsForm);
    this.appConfig = appConfigMap[app_id];
  }
  updateJson() {
    let type = this.type.toLowerCase();
    if (type == this.lastValue.type && this.level == this.lastValue.level) {
      return;
    }
    this.topologyData = this.topologyLoader.loadTopologyMinimal(
      type,
      this.level
    );
    this.topologyData.nodes = this.topologyData.nodes.map((node) => {
      return {
        ...node,
        description:
          node.color === "orange" ? this.info.service : this.info.end,
      };
    });
    this.updateNodes();
    this.updateDiagram(this.topologyData);
    if (this.appForm.get("app")?.value == 4) {
      if (this.topologyForm.get("type")?.value == "Star") {
        this.appSettingsForm.get("endnode1").patchValue("node1");
        this.appSettingsForm.get("endnode2").patchValue("node3");
        this.appSettingsForm.get("endnode3").patchValue("node4");
      } else if (this.topologyForm.get("type")?.value == "Mesh") {
        this.appSettingsForm.get("endnode1").patchValue("node1");
        this.appSettingsForm.get("endnode2").patchValue("node5");
        this.appSettingsForm.get("endnode3").patchValue("node6");
      }
    }
    this.lastValue.level = this.level;
    this.lastValue.type = this.topologyForm.get("type")?.value.toLowerCase();
  }
  get app() {
    return this.appForm.get("app");
  }
  get sender() {
    return this.appSettingsForm.get("sender");
  }
  get receiver() {
    return this.appSettingsForm.get("receiver");
  }
  get node1() {
    return this.appSettingsForm.get("endnode1");
  }
  get node2() {
    return this.appSettingsForm.get("endnode2");
  }
  get node3() {
    return this.appSettingsForm.get("endnode3");
  }
  get middlenode() {
    return this.appSettingsForm.get("middleNode");
  }
  get keyLength() {
    return this.appSettingsForm.get("keyLength");
  }
  get key() {
    return this.appSettingsForm.get("key");
  }
  // checkValidity() {
  //   this.valid;
  //   let app_id = this.appForm.get("app")?.value;
  //   if (app_id != 4) {
  //     if (this.appSettingsForm.get("sender")?.value != "") {
  //       if (this.appSettingsForm.get("receiver")?.value != "") {
  //       }
  //     }
  //   }
  // }
}
function evenLengthValidator(control: FormControl) {
  const value = control.value;
  if (value.length % 2 !== 0) {
    return { evenLength: true };
  }
  return null;
}
// function lengthValidator(control: FormControl) {
//   const value = control.value;
//   if (value.length <= 10 || value.length >= 8) {
//     return { len: true };
//   }
//   return null;
// }
