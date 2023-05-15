import { HoldingDataService } from 'src/services/holding-data.service';

import { AfterViewInit, Component, ElementRef, HostListener, OnInit, ViewChild, ViewEncapsulation } from '@angular/core';
import { FormBuilder, FormControl, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';

import * as go from 'gojs'
import { ConfirmationService, MenuItem, Message, MessageService } from 'primeng/api';
import { ApiServiceService } from 'src/services/api-service.service';

import { ConditionsService } from 'src/services/conditions.service';
import { environment } from 'src/environments/environment';
import { Subscription, map } from 'rxjs';

@Component({
  selector: 'app-advanced',
  templateUrl: './advanced.component.html',
  styleUrls: ['./advanced.component.less'],
  providers: [MessageService, ConfirmationService],
  encapsulation: ViewEncapsulation.None
})
export class AdvancedComponent implements OnInit, AfterViewInit {
  app: any
  adornedpart: any
  routeFrom: string
  @ViewChild('diagramContainer') private diagramRef: ElementRef;
  private addButtonAdornment: go.Adornment;
  nodeTypeSelect: boolean = false
  private subscription: Subscription;
  logs: any
  nodesSelection = {
    sender: '',
    receiver: '',
    endNode1: '',
    endNode2: '',
    endNode3: '',
    middleNode: '',
    attack: 'none',
    numDecoy: 4,
    numCheckBits: 4,
    errorThreshold: 0.5,
    message: 'hello',
    senderId: 1010,
    receiverId: 1011,
    belltype: 10,
    channel: 1,

  }
  detectorProps = {
    efficiency: 1,
    countRate: 25000000,
    timeResolution: 150
  }
  lightSourceProps = {
    frequency: 193548387096774.2,
    wavelength: 1550,
    bandwidth: 0,
    meanPhotonNum: 0.1,
    phaseError: 0
  }
  simulator = {
    value: 'version1',
    options: [{
      header: 'Version 1', value: 'version1'
    },
    {
      header: 'Version 2', value: 'version2'
    }]
  };
  link_array: any = []
  app_id: any
  checked: boolean = false;
  nodesData: any = {}
  serviceNodes: any[] = []
  endNodes: any[] = []
  step: any
  popover2: string = "Click on component's name to modify its name."
  cc: any = []
  nodeWithKey: any
  paramsSet = new Map()
  topology: any
  appSettings: any
  nodeKey: any
  spinner: boolean = false
  e2e: any;
  graphModel: any
  nodes: any = []
  selectedNode1: any
  displayPosition: boolean;
  items: MenuItem[];
  position: string;
  node: any = {};
  toolbox = this.fb.group({
    'attenuation': new FormControl('0.1'),
    'distance': new FormControl('70')
  })
  attackOptions = ['DoS', "EM", "IR", "none"]
  bellTypeOptions = ["00", "01", "10", "11"];
  channelOptions = [1, 2, 3]
  breadcrumbItems: MenuItem[]
  public selectedNode: any;
  public selectedLink: any
  public myDiagram: any
  public myPalette: go.Palette
  public savedModel: any
  links: any = [];
  application: any;
  activeIndex: number;
  appSettingsForm = this.fb.group({
    'sender': ['', Validators.required],
    'receiver': ['', Validators.required],
    'startTime': new FormControl('1'),
    'size': new FormControl('6'),
    'targetFidelity': new FormControl('0.5'),
    'timeout': new FormControl('1'),
    'keyLength': new FormControl('5'),
    'message': new FormControl('10011100', evenLengthValidator),
    'sequenceLength': new FormControl('2'),
    'amplitude1': new FormControl('0.70710678118+0j'),
    'amplitude2': new FormControl('0-0.70710678118j'),
    'endnode1': new FormControl(''),
    'endnode2': new FormControl(''),
    'endnode3': new FormControl(''),
    'middleNode': new FormControl(''),
    'message1': new FormControl(''),
    'message2': new FormControl(''),
    'num_photons': new FormControl(''),
    'inputMessage': new FormControl(''),
    'ip2message': new FormControl(''),
    'senderId': new FormControl('1010'),
    'receiverId': new FormControl('1011'),
    'numCheckBits': new FormControl(''),
    'numDecoy': new FormControl(''),
    'attack': new FormControl(''),
    'belltype': [],
    'channel': [],
    'errorthreshold': []
  })
  app_data: { 1: string; 2: string; 3: string; 4: string; 5: string; 6: string; 7: string; 8: string; 9: string; 10: string; };
  constructor(private fb: FormBuilder, private con: ConditionsService, private messageService: MessageService, private apiService: ApiServiceService, private holdingData: HoldingDataService, private _route: Router, private modal: NgbModal, private confirmationService: ConfirmationService) {
  }
  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    this.step = 0;
  }
  ngAfterViewInit(): void {
    this.initDiagram();
    this.updateNodes()
  }

  allowBitsInput($event: any) {
    if ($event.key.match(/[0-1]*/)['0']) { }
    else {
      $event.preventDefault();
    }
  }
  selectNodeType(adornedpart: any) {
    this.nodeTypeSelect = true;
    this.adornedpart = adornedpart
  }
  updateNodes() {
    var nodesArray = this.myDiagram.model.nodeDataArray
    this.serviceNodes = [];
    this.endNodes = [];
    this.nodes = [];
    for (let i = 0; i < nodesArray.length; i++) {
      const nodereq = {
        "Name": nodesArray[i].name,
        "Type": nodesArray[i].properties[0].propValue.toLowerCase(),
        "noOfMemory": nodesArray[i].properties[1].propValue,
        "memory": {
          'frequency': nodesArray[i].memory[0].propValue,
          'expiry': nodesArray[i].memory[1].propValue,
          'efficiency': nodesArray[i].memory[2].propValue,
          'fidelity': nodesArray[i].memory[3].propValue
        }
      };
      this.nodesData[nodesArray[i].key] = nodereq;
      if ((this.myDiagram.model.nodeDataArray[i] as any).key in this.nodesData) {
        this.nodes.push(this.nodesData[(this.myDiagram.model.nodeDataArray[i] as any).key])
      }
    }
    for (const [key, value] of Object.entries(this.nodesData)) {
      if (value["Type"].toLowerCase() == 'end') {
        this.endNodes.push(value)
      } else if (value["Type"].toLowerCase() == 'service') {
        this.serviceNodes.push(value)
      }
    }
    console.log(this.endNodes)
    // this.appSettingsForm.reset()
    this.nodesSelection.sender = this.endNodes[0].Name
    this.nodesSelection.receiver = this.endNodes.length > 1 ? this.endNodes[1].Name : this.endNodes[0].Name
    this.nodesSelection.endNode1 = this.endNodes[0].Name
    this.nodesSelection.endNode2 = this.endNodes.length > 1 ? this.endNodes[1].Name : this.endNodes[0].Name
    this.nodesSelection.endNode3 = this.endNodes.length > 2 ? this.endNodes[2].Name : this.endNodes.length == 2 ? this.endNodes[1].Name : this.endNodes[0].Name
    this.nodesSelection.middleNode = this.serviceNodes.length > 0 ? this.serviceNodes[0].Name : ''
    // this.appSettingsForm.get('sender')?.reset()
    // this.appSettingsForm.get('receiver')?.reset()
    // this.appSettingsForm.get('receiver')?.patchValue(this.endNodes[1])

  }
  ngOnInit(): void {
    this.e2e = {
      targetFidelity: 0.5,
      size: 6
    }
    // init for these samples -- you don't need to call this
    this.activeIndex = 0
    this.con.getAppList().pipe(map((d: any) => d.appList)).subscribe((result: any) => this.app_data = result);
    this.app_id = localStorage.getItem('app_id')
    this.application = localStorage.getItem('app')
    this.routeFrom = this.holdingData.getRoute();
    this.app = Number(localStorage.getItem('app_id'))
    this.simulator.options = this.app == 2 ? [{ header: 'Version 1', value: 'version1' }, { header: 'Version 2', value: 'version2' }] : [{
      header: 'Version 1', value: 'version1'
    }]
  }
  changeApp() {
    localStorage.setItem("app_id", this.app)
    this.app_id = this.app
    this.simulator.options = this.app == 2 ? [{ header: 'Version 1', value: 'version1' }, { header: 'Version 2', value: 'version2' }] : [{
      header: 'Version 1', value: 'version1'
    }]

  }
  routeTo() {
    this._route.navigate(['/minimal'])
  }
  parameters() {
    this.app_id = localStorage.getItem('app_id')
    if (this.app_id == 5 || this.app_id == 6 || this.app_id == 10 || this.app_id == 7) {
      if (this.appSettingsForm.get('message')?.value.length % 2 != 0) {
        alert("Message length should be even ");
        // this.spinner = false
        return
      }
    }
    if (this.app_id == 9) {
      if (this.appSettingsForm.get('inputMessage')?.value == '') {
        alert("Message is required");
        return
      }
    }
    if (this.app_id != 4) {
      if (this.nodesSelection.sender == '') {
        alert("Please select a sender")
        return
      }
      else if (this.nodesSelection.receiver == '') {
        alert("Please select a receiver.")
        return;
      }
      else if (this.nodesSelection.sender == this.nodesSelection.receiver) {
        alert("Sender and Receiver cannot be same node");
        return;
      }
    }
    if (this.app_id == 4) {
      let middleNode = this.appSettingsForm.get('middleNode')?.value
      console.log(this.nodesSelection.endNode1)
      console.log(this.nodesSelection.endNode2)
      console.log(this.nodesSelection.endNode3)
      if (this.nodesSelection.endNode1 == '' || this.nodesSelection.endNode2 == '' || this.nodesSelection.endNode3 == '' || middleNode == '') {
        alert('Please select End Nodes.')
        return;
      }
      if (this.nodesSelection.endNode1 == this.nodesSelection.endNode2
        || this.nodesSelection.endNode2 == this.nodesSelection.endNode3
        || this.nodesSelection.endNode3 == this.nodesSelection.endNode1) {
        alert("End Nodes cannot be same node");
        return;
      }
    }
    for (let i = 0; i < this.myDiagram.model.nodeDataArray.length; i++) {
      if (!((this.myDiagram.model.nodeDataArray[i] as any).key in this.nodesData)) {

        alert("Please configure the node named:" + (this.myDiagram.model.nodeDataArray[i] as any).text);
        return;
      };
    }
    this.myDiagram.model.modelData.position = go.Point.stringify(this.myDiagram.position);
    this.savedModel = this.myDiagram.model;
    this.graphModel = this.myDiagram.model.nodeDataArray
    this.links = []
    var linkarray: any[]
    if (this.savedModel.linkDataArray.length > this.links.length) {
      for (var i = 0; i < this.savedModel.linkDataArray.length; i++) {
        linkarray = []
        var from = this.myDiagram.model.findNodeDataForKey(this.savedModel.linkDataArray[i].from).name
        var to = this.myDiagram.model.findNodeDataForKey(this.savedModel.linkDataArray[i].to).name
        linkarray.push(from);
        linkarray.push(to);
        let linkData = {
          Nodes: linkarray,
          Attenuation: 0.1,
          Distance: 70
        }
        this.links.push(linkData)
      }
    }
    this.nodes = []
    console.log(this.nodesData)
    for (const [key, value] of Object.entries(this.nodesData)) {
      this.nodes.push(value)
    }

    this.spinner = true;
    this.displayPosition = false
    this.app_id = localStorage.getItem('app_id')
    if (!this.app_id) {
      this._route.navigate(['/applications'])
    }
    this.app_id = Number(this.app_id)
    this.cc = []
    console.log(this.nodes)
    this.cc = this.holdingData.getClassicalConnections(this.nodes)
    this.topology = {
      nodes: this.nodes,
      quantum_connections: this.links,
      classical_connections: this.cc,
      detector_properties: {
        efficiency: this.detectorProps.efficiency,
        count_rate: this.detectorProps.countRate,
        time_resolution: this.detectorProps.timeResolution
      },
      light_source_properties: {
        frequency: this.lightSourceProps.frequency,
        wavelength: this.lightSourceProps.wavelength,
        bandwidth: this.lightSourceProps.bandwidth,
        mean_photon_num: this.lightSourceProps.meanPhotonNum,
        phase_error: this.lightSourceProps.phaseError,
      }
    }
    const appConfig =
    {
      1: {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        keyLength: Number(this.appSettingsForm.get('keyLength')?.value)
      },

      2: {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        startTime: 1e12,
        size: this.appSettingsForm.get('size')?.value,
        priority: 0,
        targetFidelity: this.e2e.targetFidelity,
        timeout: this.appSettingsForm.get('timeout')?.value + 'e12'
      }
      , 3: {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        amplitude1: this.appSettingsForm.get('amplitude1')?.value,
        amplitude2: this.appSettingsForm.get('amplitude2')?.value
      }, 4: {
        endnode1: this.appSettingsForm.get('endnode1')?.value,
        endnode2: this.appSettingsForm.get('endnode2')?.value,
        endnode3: this.appSettingsForm.get('endnode3')?.value,
        middlenode: this.appSettingsForm.get('middleNode')?.value,
      }, 5:
      {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        sequenceLength: this.appSettingsForm.get('sequenceLength')?.value,
        key: this.appSettingsForm.get('message')?.value
      }, 6:
      {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        sequenceLength: this.appSettingsForm.get('sequenceLength')?.value,
        message: this.appSettingsForm.get('message')?.value,
      }, 7:
      {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        message: this.appSettingsForm.get('message')?.value
      },
      8:
      {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        message1: this.appSettingsForm.get('message1')?.value,
        message2: this.appSettingsForm.get('message2')?.value,
        attack: ''
      }, 9:
      {
        sender: this.nodesSelection.sender,
        receiver: this.nodesSelection.receiver,
        message: this.appSettingsForm.get('inputMessage')?.value,
        attack: this.appSettingsForm.get('attack')?.value
      }, 10:
      {
        sender: {
          node: this.nodesSelection.sender,
          message: this.appSettingsForm.get('message')?.value,
          userID: `${this.nodesSelection.senderId}`,
          num_check_bits: this.nodesSelection.numCheckBits,
          num_decoy_photons: this.nodesSelection.numDecoy
        },
        receiver: {
          node: this.nodesSelection.receiver,
          userID: `${this.nodesSelection.receiverId}`
        },
        bell_type: `${this.nodesSelection.belltype}`,
        error_threshold: this.nodesSelection.errorThreshold,
        attack: this.nodesSelection.attack,
        channel: this.nodesSelection.channel
      }
    }
    this.appSettings = appConfig[this.app_id]
    var req = {
      "application": this.app_id,
      "topology": this.topology,
      "appSettings": this.appSettings
    }
    // let url = this.simulator.value == 'version1' ? environment.apiUrl : this.simulator.value == 'version2' ? environment.apiUrlNew : null;
    let url = environment.apiUrlNew;
    // this.apiService.getStream().subscribe(data => { this.logs = data; });
    // whatever your request data is
    this.apiService.advancedRunApplication(req, url).subscribe({
      next: (response) => {
        console.log(response);
        this.con.setResult(response)
      },
      error: (error) => {
        console.error(`Error: ${error}`);
        this.spinner = false;
      },
      complete: () => {
        this.spinner = false;
        this._route.navigate(['/results'])
      }
    });
    // this.apiService.runApplication(req, url).subscribe((result: any) => {
    //   this.spinner = true;
    //   this.con.setResult(result)
    // }, (error) => {
    //   this.spinner = false
    //   console.error(error)
    //   // alert("Error has occurred:" + "" + error.status + "-" + error.statusText)
    // }, () => {
    //   this.spinner = false
    //   this._route.navigate(['/results'])
    // })
  }
  addNode(nodetype: string) {
    var adornedPart = this.adornedpart
    const newKey = this.myDiagram.model.nodeDataArray[this.myDiagram.model.nodeDataArray.length - 1].key
    const newNode = {
      key: newKey + 1,
      name: `node${newKey + 1}`,
      color: nodetype == 'Service' ? 'lightsalmon' : nodetype == 'End' ? 'lightblue' : null,
      properties: [
        { propName: "Type", propValue: nodetype, nodeType: true },
        { propName: "No of Memories", propValue: 500, numericValueOnly: true }
      ],
      memory: [
        { propName: "Frequency (Hz)", propValue: 2000, numericValueOnly: true },
        { propName: "Expiry (ms)", propValue: -1, numericValueOnly: true },
        { propName: "Efficiency", propValue: 1, decimalValueAlso: true },
        { propName: "Fidelity", propValue: 0.93, decimalValueAlso: true }
      ]
    };
    this.myDiagram.startTransaction('Add node and link');
    this.myDiagram.model.addNodeData(newNode);
    this.myDiagram.model.addLinkData({ from: adornedPart.data.key, to: newNode.key });
    this.myDiagram.commitTransaction('Add node and link');
    this.myDiagram.zoomToFit();
    this.nodeTypeSelect = false
    this.updateNodes()
  }
  load() {
    this.myDiagram.model = go.Model.fromJson(this.savedModel)
    this.loadDiagramProperties();  // do this after the Model.modelData has been brought into memory
  }
  loadDiagramProperties() {
    var pos = this.myDiagram.model.modelData.position;
    if (pos) this.myDiagram.initialPosition = go.Point.parse(pos);
    this.myDiagram.contentAlignment = go.Spot["Center"];
  }

  activeindex(data: any) {
    if (data == 'next') {
      if (this.activeIndex <= 1) {
        this.activeIndex++;
      }

    } else if (data == 'prev') {
      if (this.activeIndex >= 1) {
        this.activeIndex--;
      }
    }
  }
  // Define a method to delete a node
  deleteNode(nodeData: any) {
    const diagram = this.myDiagram;
    if (diagram.model.nodeDataArray.length > 1) {
      diagram.startTransaction('delete node');
      // find the node in the diagram by its data
      const node = diagram.findNodeForData(nodeData);
      // remove the node from the diagram
      diagram.remove(node);
      diagram.commitTransaction('delete node');
      this.myDiagram.zoomToFit();
    }
  }
  calculateFrequency() {
    const speedOfLight = 3e17; // speed of light in nm/s
    this.lightSourceProps.frequency = speedOfLight / this.lightSourceProps.wavelength;
    // console.log(this.lightSourceProps.frequency)
  }
  calculateWavelength() {
    const speedOfLight = 3e17; // speed of light in nm/s
    this.lightSourceProps.wavelength = speedOfLight / this.lightSourceProps.frequency;
    // console.log(this.lightSourceProps.wavelength)
  }
  get middlenode() {
    return this.appSettingsForm.get('middleNode')
  }
  get keyLength() {
    return this.appSettingsForm.get('keyLength')
  }
  get key() {
    return this.appSettingsForm.get('key')
  }
  initDiagram() {
    const $ = go.GraphObject.make;


    this.myDiagram = $(go.Diagram, this.diagramRef.nativeElement, {
      initialContentAlignment: go.Spot.Center,
      'undoManager.isEnabled': true,
      'initialAutoScale': go.Diagram.Uniform, // Ensures the myDiagram fits the viewport
      'allowZoom': true, // Disables zooming
      layout: $(go.ForceDirectedLayout)
    });


    function isPositiveNumber(val: any) {
      console.log(val)
      const regex = /^\d+$/;
      return regex.test(val);
    }
    function isDecimalNumber(val: any) {
      const regex = /^\d+(\.\d*)?$/;
      return regex.test(val);
    }

    var memoryTemplate =
      $(go.Panel, "Horizontal",
        $(go.TextBlock,
          { isMultiline: false, editable: false },
          new go.Binding("text", "propName").makeTwoWay(),
          new go.Binding("isUnderline", "scope", s => s[0] === 'c')
        ),
        // property type, if known
        $(go.TextBlock, "",
          new go.Binding("text", "propValue", t => t ? ": " : "")),
        $(go.Panel, "Auto",
          $(go.Shape, "RoundedRectangle", { fill: "white" }),
          $(go.TextBlock,
            { margin: 1, isMultiline: false, editable: true },
            new go.Binding("text", "propValue").makeTwoWay()
          )
        ),
        // property default value, if any
        $(go.TextBlock,
          { isMultiline: false, editable: false },
          new go.Binding("text", "default", s => s ? " = " + s : "")
        )
      );
    var propertyTemplate =
      $(go.Panel, "Horizontal",
        $(go.TextBlock,
          { isMultiline: false, editable: false },
          new go.Binding("text", "propName").makeTwoWay(),
          new go.Binding("isUnderline", "scope", s => s[0] === 'c')
        ),
        // property type, if known
        $(go.TextBlock, "",
          new go.Binding("text", "propValue", t => t ? ": " : "")),
        $(go.Panel, "Auto",
          $(go.Shape, "RoundedRectangle", { fill: "white" }),
          $(go.TextBlock,
            { margin: 1, isMultiline: false, editable: true },
            new go.Binding("text", "propValue").makeTwoWay()
          )
        ),
        // property default value, if any
        $(go.TextBlock,
          { isMultiline: false, editable: false },
          new go.Binding("text", "default", s => s ? " = " + s : "")
        )
      );

    this.myDiagram.nodeTemplate =
      $(go.Node, "Auto",
        {
          locationSpot: go.Spot.Center,
          fromSpot: go.Spot.AllSides,
          toSpot: go.Spot.AllSides
        },
        $(go.Shape, "RoundedRectangle", { strokeWidth: 1, stroke: "black" },
          // Shape.fill is bound to Node.data.color
          new go.Binding("fill", "color")),
        $(go.Panel, "Table",
          { defaultRowSeparatorStroke: "black" },
          // header
          $(go.TextBlock,
            {
              row: 0, columnSpan: 2, margin: 3, alignment: go.Spot.Center,
              font: "bold 12pt sans-serif",
              isMultiline: false, editable: true
            },
            new go.Binding("text", "name").makeTwoWay()),
          // properties
          $(go.TextBlock, "Properties",
            { row: 1, font: "italic 10pt sans-serif" },
            new go.Binding("visible", "visible", v => !v).ofObject("PROPERTIES")),
          $(go.Panel, "Vertical", { name: "PROPERTIES" },
            new go.Binding("itemArray", "properties"),
            {
              row: 1, margin: 3, stretch: go.GraphObject.Fill,
              defaultAlignment: go.Spot.Left, background: "lightblue",
              itemTemplate: propertyTemplate
            }, new go.Binding("background", "color")
          ),
          $("PanelExpanderButton", "PROPERTIES",
            { row: 1, column: 1, alignment: go.Spot.TopRight, visible: false },
            new go.Binding("visible", "properties", arr => arr.length > 0)),
          // methods
          $(go.TextBlock, "Memory",
            { row: 2, font: "italic 10pt sans-serif" },
            new go.Binding("visible", "visible", v => !v).ofObject("MEMORY")),
          $(go.Panel, "Vertical", { name: "MEMORY" },
            new go.Binding("itemArray", "memory"),
            {
              row: 2, margin: 3, stretch: go.GraphObject.Fill,
              defaultAlignment: go.Spot.Left, background: "lightblue",
              itemTemplate: memoryTemplate
            },
            new go.Binding("background", "color")
          ),
          $("PanelExpanderButton", "MEMORY",
            { row: 2, column: 1, alignment: go.Spot.Right, visible: false },
            new go.Binding("visible", "memory", arr => arr.length > 0)),
          $(go.Panel, 'Spot',
            {
              alignment: go.Spot.Right,
              alignmentFocus: go.Spot.Left,
              click: (e: any, obj: any) => this.selectNodeType(obj.part)
            },
            $(go.Shape,
              {
                figure: 'Rectangle',
                spot1: new go.Spot(0, 0, 4, 0), spot2: new go.Spot(1, 1, -1, -1),
                fill: 'transparent', strokeWidth: 0,
                desiredSize: new go.Size(20, 20),
                margin: new go.Margin(0, 0, 0, 20),
                mouseEnter: (e: any, obj: any) => {
                  // obj.fill = 'rgba(128,128,128,0.7)';
                },
                mouseLeave: (e: any, obj: any) => {
                  // obj.fill = 'lighblue';
                }
              }
            ),
            $(go.TextBlock, '+', { font: 'bold 10pt sans-serif', margin: new go.Margin(0, 0, 0, 5) })
          ),
          $(go.Panel, "Spot",
            {
              alignment: go.Spot.Left,
              alignmentFocus: go.Spot.Right,
              click: (e: any, obj: any) => this.deleteNode(obj.part.data)
            },
            $(go.Shape,
              {
                figure: 'Rectangle',
                spot1: new go.Spot(0, 0, 0, 1), spot2: new go.Spot(1, 1, -1, -1),
                fill: 'transparent', strokeWidth: 0,
                desiredSize: new go.Size(30, 30),
                margin: new go.Margin(0, 0, 0, 2),
                mouseEnter: (e: any, obj: any) => {
                  // obj.fill = 'lightblue';
                },
                mouseLeave: (e: any, obj: any) => {
                  // obj.fill = 'lightblue';
                }
              }
            ),
            $(go.TextBlock, '-', { font: 'bold 10pt sans-serif', margin: new go.Margin(0, 5, 0, 0) })
          )
        )
      );
    this.myDiagram.linkTemplate =
      $(go.Link,
        $(go.Shape),
        $(go.Shape, { toArrow: 'Standard' })
      );
    var nodeDataArray = [
      {
        key: 1,
        name: "node1",
        color: "lightblue",
        properties: [
          { propName: "Type", propValue: "End", nodeType: true },
          { propName: "No of Memories", propValue: 500, numericValueOnly: true }
        ],
        memory: [
          { propName: "Frequency (Hz)", propValue: 2000, numericValueOnly: true },
          { propName: "Expiry (ms)", propValue: -1, numericValueOnly: true },
          { propName: "Efficiency", propValue: 1, decimalValueAlso: true },
          { propName: "Fidelity", propValue: 0.93, decimalValueAlso: true }
        ]
      }
    ];


    this.myDiagram.model = new go.GraphLinksModel(nodeDataArray, []);
    this.myDiagram.addDiagramListener("TextEdited", (e: any) => {
      const tb = e.subject;
      const nodeData = tb.part && tb.part.data;
      if (nodeData && nodeData.properties) {
        const editedProperty = nodeData.properties.find((prop: any) => prop.propValue.toString() === tb.text);
        if (editedProperty && editedProperty.numericValueOnly) {
          if (!isPositiveNumber(tb.text)) {
            tb.text = e.parameter; // Revert to the previous text value
          }
        }
        if (editedProperty && editedProperty.nodeType) {
          if (tb.text != 'Service' || tb.text != 'End') {
            tb.text = e.parameter
          }
        }
      }
      if (nodeData && nodeData.memory) {
        const editedProperty = nodeData.memory.find((prop: any) => prop.propValue.toString() === tb.text);
        if (editedProperty && editedProperty.decimalValueAlso) {
          if (!isDecimalNumber(tb.text)) {
            tb.text = e.parameter; // Revert to the previous text value
          }
        }
        if (editedProperty && editedProperty.numericValueOnly) {
          if (!isPositiveNumber(tb.text)) {
            tb.text = e.parameter; // Revert to the previous text value
          }
        }
      }
      this.updateNodes()
    });
  }
  public zoomIn() {
    const diagram = this.myDiagram;
    const zoom = diagram.commandHandler.zoomFactor;
    diagram.commandHandler.zoomTo(zoom + 0.1, diagram.lastInput.documentPoint);
  }

  public zoomOut() {
    const diagram = this.myDiagram;
    const zoom = diagram.commandHandler.zoomFactor;
    diagram.commandHandler.zoomTo(Math.max(zoom - 0.1, 0.1), diagram.lastInput.documentPoint);
  }

}
function evenLengthValidator(control: FormControl) {
  const value = control.value;
  if (value.length % 2 !== 0) {
    return { evenLength: true };
  }
  return null;
}


