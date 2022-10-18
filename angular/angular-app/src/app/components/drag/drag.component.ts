import { HttpHeaders } from '@angular/common/http';
import { AfterViewInit, Component, OnChanges, OnInit, SimpleChanges, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import * as go from 'gojs'
import { MenuItem, MessageService } from 'primeng/api';
import { ApiServiceService } from 'src/services/api-service.service';
//import { Interface } from 'readline';
import { ConditionsService } from 'src/services/conditions.service';
@Component({
  selector: 'app-drag',
  templateUrl: './drag.component.html',
  styleUrls: ['./drag.component.less'],
  providers: [MessageService],
  encapsulation: ViewEncapsulation.None
})
export class DragComponent implements OnInit, AfterViewInit, OnChanges {
  app_id: any

  ip1: any
  e91: any
  e2e: any;
  pingPong: any
  teleportation: any
  ghz: any
  firstqsdc: any

  graphModel: any
  nodes: any = []
  selectedNode1: any
  displayPosition: boolean;
  items: MenuItem[];
  position: string;
  node: any = {};
  toolbox: any
  public selectedNode: any;
  visibleSideNav: boolean
  public myDiagram: go.Diagram
  public myPalette: go.Palette
  public myRotate: go.RotatingTool
  public savedModel: any = {
    class: "go.GraphLinksModel",
    linkFromPortIdProperty: "fromPort",
    linkToPortIdProperty: "toPort",
    nodeDataArray: [
    ],
    linkDataArray: [
    ]
  }


  constructor(private fb: FormBuilder, private con: ConditionsService, private messageService: MessageService, private apiService: ApiServiceService) { }

  ngOnChanges(changes: SimpleChanges): void {
    console.log(this.myDiagram.nodes)
  }
  ngAfterViewInit(): void {
    this.myDiagram.addDiagramListener("ChangedSelection", function (event) {

      // console.log(node.key);
      // console.log(node.name)
    })

    // go.Diagram.inherit(go, go.RotatingTool);
    // this.TopRotatingTool.prototype.updateAdornments = function (part: any) {
    //   go.RotatingTool.prototype.updateAdornments.call(this, part);
    //   var adornment = part.findAdornment("Rotating");
    //   if (adornment !== null) {
    //     adornment.location = part.rotateObject.getDocumentPoint(new go.Spot(0.5, 0, 0, -30));  // above middle top
    //   }
    // };

    // /** @override */
    // this.TopRotatingTool.prototype.rotate = function (newangle: any) {
    //   go.RotatingTool.prototype.rotate.call(this, newangle + 90);
    // };
  }

  ngOnInit(): void {

    // init for these samples -- you don't need to call this
    var $ = go.GraphObject.make;  // for conciseness in defining templates

    this.myDiagram =
      $(go.Diagram, "myDiagramDiv",  // must name or refer to the DIV HTML element
        {
          grid: $(go.Panel, "Grid",
            $(go.Shape, "LineH", { stroke: "lightgray", strokeWidth: 0.5 }),
            $(go.Shape, "LineH", { stroke: "gray", strokeWidth: 0.5, interval: 10 }),
            $(go.Shape, "LineV", { stroke: "lightgray", strokeWidth: 0.5 }),
            $(go.Shape, "LineV", { stroke: "gray", strokeWidth: 0.5, interval: 10 })
          ),
          allowDrop: true,  // must be true to accept drops from the Palette
          "draggingTool.dragsLink": true,
          "draggingTool.isGridSnapEnabled": true,
          "linkingTool.isUnconnectedLinkValid": true,
          "linkingTool.portGravity": 20,
          "relinkingTool.isUnconnectedLinkValid": true,
          "relinkingTool.portGravity": 20,
          "relinkingTool.fromHandleArchetype":
            $(go.Shape, "Diamond", { segmentIndex: 0, cursor: "pointer", desiredSize: new go.Size(8, 8), fill: "tomato", stroke: "darkred" }),
          "relinkingTool.toHandleArchetype":
            $(go.Shape, "Diamond", { segmentIndex: -1, cursor: "pointer", desiredSize: new go.Size(8, 8), fill: "darkred", stroke: "tomato" }),
          "linkReshapingTool.handleArchetype":
            $(go.Shape, "Diamond", { desiredSize: new go.Size(7, 7), fill: "lightblue", stroke: "deepskyblue" }),
          // rotatingTool: go.RotatingTool,  // defined below
          // "rotatingTool.snapAngleMultiple": 15,
          // "rotatingTool.snapAngleEpsilon": 15,
          // "undoManager.isEnabled": true
        });

    // when the document is modified, add a "*" to the title and enable the "Save" button
    this.myDiagram.addDiagramListener("Modified", e => {
      var button = document.getElementById("SaveButton") as HTMLButtonElement;
      if (button) button.disabled = !this.myDiagram.isModified;
      var idx = document.title.indexOf("*");
      if (this.myDiagram.isModified) {
        if (idx < 0) document.title += "*";
      } else {
        if (idx >= 0) document.title = document.title.slice(0, idx);
      }
    });

    // Define a function for creating a "port" that is normally transparent.
    // The "name" is used as the GraphObject.portId, the "spot" is used to control how links connect
    // and where the port is positioned on the node, and the boolean "output" and "input" arguments
    // control whether the user can draw links from or to the port.
    function makePort(name: any, spot: any, output: any, input: any) {
      // the port is basically just a small transparent square
      return $(go.Shape, "Circle",
        {
          fill: null,  // not seen, by default; set to a translucent gray by showSmallPorts, defined below
          stroke: null,
          desiredSize: new go.Size(7, 7),
          alignment: spot,  // align the port on the main Shape
          alignmentFocus: spot,  // just inside the Shape
          portId: name,  // declare this object to be a "port"
          fromSpot: spot, toSpot: spot,  // declare where links may connect at this port
          fromLinkable: output, toLinkable: input,  // declare whether the user may draw links to/from here
          cursor: "pointer"  // show a different cursor to indicate potential link point
        });
    }
    var nodeSelectionAdornmentTemplate =
      $(go.Adornment, "Auto",
        $(go.Shape, { fill: null, stroke: "blue", strokeWidth: 1.5, strokeDashArray: [4, 2] }),
        $(go.Placeholder)
      );

    var nodeResizeAdornmentTemplate =
      $(go.Adornment, "Spot",
        { locationSpot: go.Spot.Right },
        $(go.Placeholder),
        $(go.Shape, { alignment: go.Spot.TopLeft, cursor: "nw-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
        $(go.Shape, { alignment: go.Spot.Top, cursor: "n-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
        $(go.Shape, { alignment: go.Spot.TopRight, cursor: "ne-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),

        $(go.Shape, { alignment: go.Spot.Left, cursor: "w-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
        $(go.Shape, { alignment: go.Spot.Right, cursor: "e-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),

        $(go.Shape, { alignment: go.Spot.BottomLeft, cursor: "se-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
        $(go.Shape, { alignment: go.Spot.Bottom, cursor: "s-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" }),
        $(go.Shape, { alignment: go.Spot.BottomRight, cursor: "sw-resize", desiredSize: new go.Size(6, 6), fill: "lightblue", stroke: "deepskyblue" })
      );

    var nodeRotateAdornmentTemplate =
      $(go.Adornment,
        { locationSpot: go.Spot.Center, locationObjectName: "CIRCLE" },
        $(go.Shape, "Circle", { name: "CIRCLE", cursor: "pointer", desiredSize: new go.Size(7, 7), fill: "lightblue", stroke: "deepskyblue" }),
        $(go.Shape, { geometryString: "M3.5 7 L3.5 30", isGeometryPositioned: true, stroke: "deepskyblue", strokeWidth: 1.5, strokeDashArray: [4, 2] })
      );
    this.myDiagram.nodeTemplate =
      $(go.Node, "Spot",
        {
          click: this.nodeClicked,
          doubleClick: this.nodeClicked,
          contextMenu:
            $("ContextMenu",
              $("ContextMenuButton",
                $(go.TextBlock, "Properties"),
                { click: this.showProperties })
            )
        },
        { locationSpot: go.Spot.Center },
        new go.Binding("location", "loc", go.Point.parse).makeTwoWay(go.Point.stringify),
        { selectable: true, selectionAdornmentTemplate: nodeSelectionAdornmentTemplate },
        { resizable: true, resizeObjectName: "PANEL", resizeAdornmentTemplate: nodeResizeAdornmentTemplate },
        { rotatable: true, rotateAdornmentTemplate: nodeRotateAdornmentTemplate },
        new go.Binding("angle").makeTwoWay(),
        // the main object is a Panel that surrounds a TextBlock with a Shape
        $(go.Panel, "Auto",
          { name: "PANEL" },
          new go.Binding("desiredSize", "size", go.Size.parse).makeTwoWay(go.Size.stringify),
          $(go.Shape, "Rectangle",  // default figure
            {
              portId: "", // the default port: if no spot on link data, use closest side
              fromLinkable: true, toLinkable: true, cursor: "pointer",
              fill: "white",  // default color
              strokeWidth: 2
            },
            new go.Binding("figure"),
            new go.Binding("fill")
          ),
          new go.Binding("strokeDashArray", "dash")),
        $(go.TextBlock,
          {
            font: "bold 11pt Helvetica, Arial, sans-serif",
            margin: 8,
            maxSize: new go.Size(160, NaN),
            wrap: go.TextBlock.WrapFit,
            editable: true
          },
          new go.Binding("text").makeTwoWay())
      ),
      // four small named ports, one on each side:
      makePort("T", go.Spot.Top, false, true),
      makePort("L", go.Spot.Left, true, true),
      makePort("R", go.Spot.Right, true, true),
      makePort("B", go.Spot.Bottom, true, false),
    { // handle mouse enter/leave events to show/hide the ports
      mouseEnter: function (e: any, node: any) { showSmallPorts(node, true); },
      mouseLeave: function (e: any, node: any) { showSmallPorts(node, false); }
    }

    var linkSelectionAdornmentTemplate =
      $(go.Adornment, "Link",
        $(go.Shape,
          // isPanelMain declares that this Shape shares the Link.geometry
          { isPanelMain: true, fill: null, stroke: "deepskyblue", strokeWidth: 0 })  // use selection object's strokeWidth
      );

    this.myDiagram.linkTemplate =
      $(go.Link,  // the whole link panel
        { selectable: true, selectionAdornmentTemplate: linkSelectionAdornmentTemplate },
        { relinkableFrom: true, relinkableTo: true, reshapable: false },
        {
          routing: go.Link.AvoidsNodes,
          curve: go.Link.JumpOver,
          corner: 5,
          toShortLength: 4
        },
        new go.Binding("points").makeTwoWay(),
        $(go.Shape,  // the link path shape
          { isPanelMain: true, strokeWidth: 2 },
          new go.Binding("stroke", "color")),
        // $(go.Shape,  // the link path shape
        //   { isPanelMain: true, strokeWidth: 2 }),
        $(go.Shape,  // the arrowhead
          { toArrow: "Standard", stroke: null },
          new go.Binding('fill', 'color')),
        $(go.Panel, "Auto",
          new go.Binding("visible", "isSelected").ofObject(),
          $(go.Shape, "RoundedRectangle",  // the link shape
            { fill: "#F8F8F8", stroke: null }),
          $(go.TextBlock,
            {
              textAlign: "center",
              font: "10pt helvetica, arial, sans-serif",
              stroke: "#919191",
              margin: 2,
              minSize: new go.Size(10, NaN),
              editable: true
            },
            new go.Binding("text").makeTwoWay())
        )
      );
    this.myPalette =
      $(go.Palette, "myPaletteDiv",  // must name or refer to the DIV HTML element
        {
          maxSelectionCount: 1,
          nodeTemplateMap: this.myDiagram.nodeTemplateMap,  // share the templates used by myDiagram
          linkTemplate: // simplify the link template, just in this Palette
            $(go.Link,
              { // because the GridLayout.alignment is Location and the nodes have locationSpot == Spot.Center,
                // to line up the Link in the same manner we have to pretend the Link has the same location spot
                locationSpot: go.Spot.Center,
                selectionAdornmentTemplate:
                  $(go.Adornment, "Link",
                    { locationSpot: go.Spot.Center },
                    $(go.Shape,
                      { isPanelMain: true, fill: null, stroke: "deepskyblue", strokeWidth: 0 }),
                    $(go.Shape,  // the arrowhead
                      { toArrow: "Standard", stroke: "black", strokeWidth: 4 }),
                    $(go.Shape,  // the arrowhead
                      { toArrow: "Standard", stroke: "blue", strokeWidth: 4 }),
                  )
              },
              {
                routing: go.Link.AvoidsNodes,
                curve: go.Link.JumpOver,
                corner: 5,
                toShortLength: 4
              },
              new go.Binding("points"),
              $(go.Shape,  // the link path shape
                { isPanelMain: true, strokeWidth: 2 }),
              $(go.Shape,  // the arrowhead
                { toArrow: "Standard", stroke: null, strokeWidth: 2 }),
              $(go.Shape,  // the arrowhead
                { toArrow: "Standard", stroke: null, strokeWidth: 2 }),
              new go.Binding('fill', 'color'),
            ),
          model: new go.GraphLinksModel([  // specify the contents of the Palette
            { text: "Service", figure: "Circle", fill: "#00AD5F" },
            { text: "End", figure: "Circle", fill: "#CE0620" },
            // { text: "Comment", figure: "RoundedRectangle", fill: "lightyellow" }
          ], [
            // the Palette also has a disconnected Link, which the user can drag-and-drop
            { text: "QC", points: new go.List(go.Point).addAll([new go.Point(0, 0), new go.Point(30, 0), new go.Point(30, 40), new go.Point(60, 40)]) },
            { color: "blue", text: "VC", points: new go.List(go.Point).addAll([new go.Point(0, 0), new go.Point(30, 0), new go.Point(30, 40), new go.Point(60, 40)]) }
          ])
        });
    this.toolbox = this.fb.group({
      'name': new FormControl(''),
      'noOfMemories': new FormControl(''),
      'memoryFidelity': new FormControl('')
    })
    this.e2e = this.fb.group({
      'sender': new FormControl(''),
      'receiver': new FormControl(''),
      'startTime': new FormControl(''),
      'size': new FormControl(''),
      'priority': new FormControl(''),
      'targetFidelity': new FormControl(''),
      'timeout': new FormControl('')
    })
    this.e91 = this.fb.group({
      'sender': new FormControl(''),
      'receiver': new FormControl(''),
      'keyLength': new FormControl('')
    })
    this.ip1 = this.fb.group({
      'sender': new FormControl(''),
      'receiver': new FormControl(''),
      'message': new FormControl('')
    })
    this.pingPong = this.fb.group({
      'sender': new FormControl(''),
      'receiver': new FormControl(''),
      'sequenceLength': new FormControl(''),
      'message': new FormControl('')
    })
    this.firstqsdc = this.fb.group({
      'sender': new FormControl(''),
      'receiver': new FormControl(''),
      'sequenceLength': new FormControl(''),
      'key': new FormControl('')
    })
    this.teleportation = this.fb.group({
      'sender': new FormControl(''),
      'receiver': new FormControl(''),
      'randomQubitAmplitude1': new FormControl(''),
      'randomQubitAmplitude2': new FormControl('')
    })
    this.ghz = this.fb.group({
      'node1': new FormControl(''),
      'node2': new FormControl(''),
      'node3': new FormControl(''),
      'middleNode': new FormControl('')
    })

  }
  selected(): any {
    console.log("selected")
  }

  save() {
    this.app_id = sessionStorage.getItem("app_id")
    console.log(this.app_id)
    //console.log(this.myDiagram.model.toJson)
    this.saveDiagramProperties();
    this.graphModel = this.myDiagram.model.nodeDataArray

    //console.log(this.graphModel)

    this.position = 'bottom';
    this.displayPosition = true;
  }
  parameters() {
    this.displayPosition = false
    var token = localStorage.getItem('access')
    var topology = { "nodes": [{ "Name": "n1", "Type": "service", "noOfMemory": 500, "memory": { "frequency": 2000, "expiry": 2000, "efficiency": 0, "fidelity": 0.93 } }, { "Name": "n2", "Type": "end", "noOfMemory": 500, "memory": { "frequency": 2000, "expiry": 2000, "efficiency": 0, "fidelity": 0.93 } }], "quantum_connections": [{ "Nodes": ["n1", "n2"], "Attenuation": 0.00001, "Distance": 70 }], "classical_connections": [{ "Nodes": ["n1", "n1"], "Delay": 0, "Distance": 1000 }, { "Nodes": ["n1", "n2"], "Delay": 1000000000, "Distance": 1000 }, { "Nodes": ["n2", "n1"], "Delay": 1000000000, "Distance": 1000 }, { "Nodes": ["n2", "n2"], "Delay": 0, "Distance": 1000 }] }
    var req = {
      "application": 1,
      "topology": topology,
      "appSettings": { "sender": "n1", "receiver": "n2", "keyLength": "5" }
    }
    this.apiService.runApplication(req).subscribe((result) => {
      console.log(result)
    })
  }
  load() {
    //var savedModel = document.getElementById("mySavedModel") as HTMLInputElement
    this.myDiagram.model = go.Model.fromJson(this.savedModel);
    this.loadDiagramProperties();  // do this after the Model.modelData has been brought into memory
  }
  saveDiagramProperties() {
    this.myDiagram.model.modelData.position = go.Point.stringify(this.myDiagram.position);
    //console.log(this.myDiagram.model.modelData.position)
  }
  showPositionDialog() {
    //var savedModel = document.getElementById("mySavedModel") as HTMLInputElement
    this.saveDiagramProperties();  // do this first, before writing to JSON
    this.savedModel = this.myDiagram.model;

    //console.log(this.savedModel)
    this.myDiagram.isModified = false;
    this.visibleSideNav = true
    this.messageService.add({
      severity: 'success', summary: 'The graph has been saved.', life: 2000
    })
  }
  loadDiagramProperties() {
    // set Diagram.initialPosition, not Diagram.position, to handle initialization side-effects
    var pos = this.myDiagram.model.modelData.position;
    if (pos) this.myDiagram.initialPosition = go.Point.parse(pos);
  }
  nodeClicked(e: any, obj: any) {
    // var evt = e.copy();
    // console.log(evt)
    var node = obj.part;
    console.log(node.data);

    // var array1 = [];
    // array1.push(array)
    // sessionStorage.setItem('node', ...array1)
    sessionStorage.setItem('nodeName', node.data.text)
    sessionStorage.setItem('nodeKey', node.data.key)
    sessionStorage.setItem('figure', node.data.figure)
    // var Node = {
    //   name: sessionStorage.getItem('nodeName'),
    //   key: sessionStorage.getItem("nodeKey")
    // }
    // console.log(Node)
    // this.selectedNode.key = "Start"
    // console.log(this.selectedNode)
    // this.con.updateNode(node.data);
    // this.con._node.subscribe((result) => {
    //   this.selectedNode = result;
    //   console.log(this.selectedNode)
    // })
    //this.selectedNode = obj.part.data
    // var type = evt.clickCount === 2 ? "Double-Clicked: " : "Clicked: ";
    // var msg = type + node.data.key + ". ";
    // console.log(msg)
  }
  showProperties(e: any, obj: any) {  // executed by ContextMenuButton
    var node = obj.part.adornedPart;
    console.log(obj.part.adornedPart)
    console.log(node)
    var msg = "Context clicked: " + node.data.key + ". ";
    msg += "Selection includes:";

    console.log(msg)
    // this.myDiagram.selection.each(function (part) {
    //   msg += " " + part.toString();
    // });
    // document.getElementById("myStatus").textContent = msg;
  }
}

function showSmallPorts(node: any, show: any) {
  node.ports.each(function (port: any) {
    if (port.portId !== "") {  // don't change the default port, which is the big shape
      port.fill = show ? "rgba(0,0,0,.3)" : null;
    }
  });
}
export class selectedNode {
  name: string;
  key: string;
  figure: string;
}

