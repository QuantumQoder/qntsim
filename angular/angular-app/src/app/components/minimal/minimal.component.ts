import { HoldingDataService } from 'src/services/holding-data.service';
import { transition } from '@angular/animations';
import { CookieService } from 'ngx-cookie-service';
import { ApiServiceService } from './../../../services/api-service.service';

import { AfterViewInit, Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import * as go from 'gojs'
import { map } from 'rxjs';
import { ConditionsService } from 'src/services/conditions.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-minimal',
  templateUrl: './minimal.component.html',
  styleUrls: ['./minimal.component.less']
})

export class MinimalComponent implements OnInit, AfterViewInit {
  data: string = '|1\\rangle'
  equation: any = [{
    header: '/assets/images/amplitude/1.jpg', value: 1,
  },
  {
    header: '/assets/images/amplitude/2.jpg', value: 2,
  },
  {
    header: '/assets/images/amplitude/3.jpg', value: 3,
  },
  {
    header: '/assets/images/amplitude/4.jpg', value: 4,
  }];

  equation1: any = [{
    header: '|1\\rangle', value: 1,
  },
  {
    header: '\\frac{|0\\rangle + |1\\rangle}{\\sqrt{2}}', value: 2,
  },
  {
    header: '\\frac{|0\\rangle - |1\\rangle}{\\sqrt{2}}', value: 3,
  },
  {
    header: '|0\\rangle', value: 4,
  }];
  radio = {
    1: true,
    2: false,
    3: false,
    4: false
  }
  amplitude: any
  e2e = {
    targetFidelity: 0.5,
    size: 6
  }
  serviceNodes: any[] = []
  endNodes: any[] = []
  topology: any
  topologyData: any
  request: Request
  spinner: boolean = false
  topologyForm: any
  appForm: any
  applist: any
  nodes: any
  appSettingsForm: any
  type = ['Star', 'Mesh'];
  level: number = 0
  cc: any[] = []
  appSettingsResult: any
  appConfig: any;
  lastValue = {
    type: 'star', level: this.level
  }

  constructor(private fb: FormBuilder, private service: ConditionsService, private route: Router, private holdingData: HoldingDataService, private api: ApiServiceService, private cookie: CookieService) { }
  ngAfterViewInit(): void {

    let urlData = this.service.jsonUrl(this.topologyForm.get('type')?.value, this.level);
    this.service.getJson(urlData.url, urlData.type).subscribe((result) => {
      this.topologyData = result;
      this.updateNodes()
    }, (error) => {
      console.log(error)
    }, () => {
      this.init(this.topologyData.nodes, this.topologyData.links)
    }
    )
  }
  toggle(data: any) {
    var content;
    var toggler;
    if (data == 1) {
      content = document.getElementById('content1') as any;
      toggler = document.getElementById('toggle-button1') as any;
      toggler.classList.toggle('active');

      if (toggler.classList.contains('active')) {
        content.style.display = 'none';
      } else {
        content.style.display = 'block';
      }
    }
    else if (data == 2) {
      content = document.getElementById('content2') as any;
      toggler = document.getElementById('toggle-button2') as any;
      toggler.classList.toggle('active');
      // content.classList.toggle('active');
      if (toggler.classList.contains('active')) {
        content.style.display = 'none';
      } else {
        content.style.display = 'block';
      }
    }
  }
  setSettings(formData: any) {
    let form = {}
    this.appSettingsForm = null
    for (let i = 0; i < formData.length; i++) {
      form[formData[i].formField] = new FormControl('')
    }
    this.appSettingsForm.addControl(form)
  }
  ngOnInit(): void {
    this.topologyForm = this.fb.group({
      'type': ['Star', Validators.required],
      'level': [0, Validators.required],
      'noOfMemories': [500, Validators.required],
      'distance': [150, [Validators.required]],
      'attenuity': [0.00001, Validators.required]
    });
    this.appForm = this.fb.group({
      'app': ['', Validators.required]
    });
    this.appSettingsForm = this.fb.group({
      'sender': ['', Validators.required],
      'receiver': ['', Validators.required],
      'targetFidelity': [0.5],
      'size': [6],
      // 'amplitude': ['', Validators.required],

    })
    // this.appSettingsForm
    this.service.getAppList().pipe(map((d: any) => d.appList)).subscribe((result: any) => this.applist = result);
    var data = this.api.getCredentials()
    this.api.accessToken(data).subscribe((result: any) => {
      localStorage.setItem('access', result.access)
    })
    this.getAppSettingsResults();
  }
  updateDiagram(data: any) {
    this.topology.model = new go.GraphLinksModel(data.nodes, data.links)
    console.log(this.topology.model.nodeDataArray);
  }
  allowBitsInput($event: any) {
    if ($event.key.match(/[0-1]*/)['0']) { }
    else {
      $event.preventDefault();
    }
  }
  updateNodes() {
    this.serviceNodes = [];
    this.endNodes = []
    for (let i = 0; i < this.topologyData.nodes.length; i++) {
      if (this.topologyData.nodes[i].color == 'lightblue') {
        this.endNodes.push(this.topologyData.nodes[i])
      } else if (this.topologyData.nodes[i].color == 'orange') {
        this.serviceNodes.push(this.topologyData.nodes[i])
      }
    }
  }
  getType($event: any) {

    this.updateJson()
  }
  levelChange() {
    this.level = this.topologyForm.get('level')?.value;
    this.updateJson();
  }
  selectAmplitude($event: any) {

  }

  e2eChange(data: string) {
    if (data == 'target') {
      this.e2e.targetFidelity = this.appSettingsForm.get('targetFidelity')?.value
    }
    else if (data == 'size') {
      this.e2e.size = this.appSettingsForm.get('size')?.value
    }
  }
  init(nodes: any, links: any) {
    var $ = go.GraphObject.make;  // for conciseness in defining templates
    this.topology = $(go.Diagram, "topology",  // create a Diagram for the DIV HTML element
      {
        initialContentAlignment: go.Spot.Center,  // center the content
        "undoManager.isEnabled": true,  // enable undo & redo
        "panningTool.isEnabled": false
        // "ViewportBoundsChanged": function (e: any) {
        //   e.diagram.toolManager.panningTool.isEnabled =
        //     !e.diagram.viewportBounds.containsRect(e.diagram.documentBounds);
        // },
      });
    // define a simple Node template
    this.topology.nodeTemplate =
      $(go.Node, "Auto",  // the Shape will go around the TextBlockcontextMenu:

        $(go.Shape, "RoundedRectangle", { strokeWidth: 0 },
          // Shape.fill is bound to Node.data.color
          new go.Binding("fill", "color")),
        new go.Binding("location", "loc", go.Point.parse),

        $(go.TextBlock,
          { margin: 8 },  // some room around the text
          // TextBlock.text is bound to Node.data.key
          new go.Binding("text", "key")),
        {
          contextMenu:     // define a context menu for each node
            $(go.Adornment, "Vertical",  // that has one button
              $("ContextMenuButton",
                $(go.TextBlock, "Set as Sender"),
                {
                  click: (e: go.InputEvent, obj: go.GraphObject) => { this.showProperties(e, obj, 'sender') }
                }),
              $("ContextMenuButton",
                $(go.TextBlock, "Set as Receiver"),
                {
                  click: (e: go.InputEvent, obj: go.GraphObject) => { this.showProperties(e, obj, 'receiver') }
                })
              // more ContextMenuButtons would go here
            )  // end Adornment
        }
      );

    this.topology.linkTemplate =
      $(go.Link,
        $(go.Shape),
      );
    this.topology.model = new go.GraphLinksModel(
      nodes, links
    )
  }
  showProperties(e: go.InputEvent, obj: any, data: String) {
    console.log(obj)
    var node = obj.part.adornedPart.data.key;
    console.log(node)
    this.nodes = this.topologyData.nodes
    this.appSettingsForm.get(data)?.patchValue(node)
  }
  getApp($event: any) {

    this.nodes = this.topologyData.nodes
    if (this.appForm.get('app')?.value == 4) {
      this.topologyForm.get('level').patchValue(2);
      this.level = 2;
      this.levelChange()
    }
    this.updateNodes()
    localStorage.setItem('app_id', this.appForm.get('app')?.value)
    this.buildForm(this.appForm.get('app')?.value)
  }
  runApp() {
    this.spinner = true;
    var linkArray = []
    // var nodeArray = []
    var linkRequestArray = []
    const nodeDataArray = this.topologyData.nodes;
    const linkDataArray = this.topologyData.links;
    const app_id = this.appForm.get('app')?.value;
    const nodeArray = nodeDataArray.map((node: any) => ({
      Name: node.key,
      Type: node.color === 'orange' ? 'service' : 'end',
      noOfMemory: this.topologyForm.get('noOfMemories')?.value,
      memory: this.service.getMemory()
    }));
    if (app_id != 4) {
      localStorage.setItem('sender', this.appSettingsForm.get('sender')?.value);
      localStorage.setItem('receiver', this.appSettingsForm.get('receiver')?.value)
    }

    localStorage.setItem('app_id', app_id);
    console.log(nodeArray)
    for (const link of linkDataArray) {
      const linkData = {
        Nodes: [link.from, link.to],
        Attenuation: this.topologyForm.get('attenuity')?.value,
        Distance: this.topologyForm.get('distance')?.value
      };
      linkRequestArray.push(linkData);
    }
    console.log(linkRequestArray);
    var cc = []
    this.cc = []
    for (var i = 0; i < nodeDataArray.length; i++) {
      for (var j = 0; j < nodeDataArray.length; j++) {
        cc.push([nodeDataArray[i].key, nodeDataArray[j].key]);
      }
    }
    if (cc.length) {
      for (var i = 0; i < cc.length; i++) {
        var [node1, node2] = cc[i];
        var [distance, delay] = node1 == node2 ? [0, 0] : [1000, 10000000000];
        this.cc.push({ Nodes: [node1, node2], Delay: delay, Distance: distance });
      }
    }
    var topology = {
      nodes: nodeArray,
      quantum_connections: linkRequestArray,
      classical_connections: this.cc
    }
    this.getAppSetting(this.appForm.get('app')?.value)
    console.log(this.appConfig)
    var request = {
      application: this.appForm.get('app')?.value,
      topology: topology,
      appSettings: this.appConfig
    }
    this.api.runApplication(request).subscribe((result) => {
      this.spinner = true;
      console.log(this.spinner)
      this.service.setResult(result)
    }, (error) => {
      this.spinner = false
      console.error(error)
    }, () => {
      this.spinner = false
      this.route.navigate(['/results'])
    })
  }
  buildForm(app: Number) {
    switch (app) {
      case 1:
        if (!this.appSettingsForm.controls['keyLength'])
          this.appSettingsForm.addControl('keyLength', new FormControl('5', Validators.required));
        break;
      case 2: console.log(app)
        break;
      case 3: console.log(app);
        break;
      case 4:
        if (!this.appSettingsForm.controls['endnode1'])
          this.appSettingsForm.addControl('endnode1', new FormControl('node1', Validators.required))
        if (!this.appSettingsForm.controls['endnode2'])
          this.appSettingsForm.addControl('endnode2', new FormControl('node3', Validators.required))
        if (!this.appSettingsForm.controls['endnode3'])
          this.appSettingsForm.addControl('endnode3', new FormControl('node4', Validators.required))
        if (!this.appSettingsForm.controls['middleNode'])
          this.appSettingsForm.addControl('middleNode', new FormControl('node2', Validators.required))
        console.log(this.appSettingsForm)
        break;
      case 5:
        if (!this.appSettingsForm.controls['key'])
          this.appSettingsForm.addControl('key', new FormControl('', [Validators.required, evenLengthValidator, Validators.minLength(8), Validators.maxLength(10)]));
        break;
      case 6:
        if (!this.appSettingsForm.controls['message'])
          this.appSettingsForm.addControl('message', new FormControl('', [Validators.required, evenLengthValidator, Validators.minLength(8), Validators.maxLength(10)]));
        break;
      case 7:
        if (!this.appSettingsForm.controls['message'])
          this.appSettingsForm.addControl('message', new FormControl('', [Validators.required, evenLengthValidator, Validators.minLength(8), Validators.maxLength(10)]));
        break;
      case 8:
        if (!this.appSettingsForm.controls['message1'])
          this.appSettingsForm.addControl('message1', new FormControl('', Validators.required));
        if (!this.appSettingsForm.controls['message2'])
          this.appSettingsForm.addControl('message2', new FormControl('', Validators.required));
        break;
      case 9:
        if (!this.appSettingsForm.controls['message'])
          this.appSettingsForm.addControl('message', new FormControl('', Validators.required));
        break;
      case 10:
        if (!this.appSettingsForm.controls['inputMessage'])
          this.appSettingsForm.addControl('inputMessage', new FormControl('', Validators.required));
        break;
    }
    console.log(this.appSettingsForm)

  }

  getAppSettingsResults() {
    this.service.getAppSetting().subscribe((results: any) => {
      this.appSettingsResult = results
    })
  }

  getAppSetting(app_id: any) {

    const appConfigMap = {
      2: {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        startTime: 1e12,
        size: this.appSettingsForm.get('size')?.value,
        priority: 0,
        targetFidelity: this.appSettingsForm.get('targetFidelity')?.value,
        timeout: 2e12
      },
      1: {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        keyLength: String(this.appSettingsForm.get('keyLength')?.value)
      },
      3: {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        amplitude1: '0.70710678118+0j',
        amplitude2: '0-0.70710678118j'
      },
      4: {
        endnode1: this.appSettingsForm.get('endnode1')?.value,
        endnode2: this.appSettingsForm.get('endnode2')?.value,
        endnode3: this.appSettingsForm.get('endnode3')?.value,
        middlenode: this.appSettingsForm.get('middleNode')?.value
      },
      5: {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        sequenceLength: 3,
        key: this.appSettingsForm.get('key')?.value
      },
      6: {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        sequenceLength: "2",
        message: this.appSettingsForm.get('message')?.value
      },
      7: {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        message: this.appSettingsForm.get('message')?.value
      },
      8: {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        message1: this.appSettingsForm.get('message1')?.value,
        message2: this.appSettingsForm.get('message2')?.value,
        num_photons: 5,
        attack: 'DoS'
      },
      9: {
        sender: 1,
        receiver: 2,
        message: this.appSettingsForm.get('message')?.value,
        attack: 'None'
      },
      10: {
        input_messages: { 2: this.appSettingsForm.get('message')?.value },
        ids: { 2: "1011", 1: "0111" },
        num_check_bits: 4,
        num_decoy: 4
      }
    };

    this.appConfig = appConfigMap[app_id];
  }
  updateJson() {
    let type = this.topologyForm.get('type')?.value.toLowerCase();
    if (type === this.lastValue.type && this.level == this.lastValue.level) {
      return;
    }
    let urlData = this.service.jsonUrl(this.topologyForm.get('type')?.value.toLowerCase(), this.level);
    this.service.getJson(urlData.url, urlData.type).subscribe((result: any) => {
      this.topologyData = result;
      console.log(this.topologyData)
      this.updateNodes()
    }, (error) => {
      console.log(error)
    }, () => {
      this.updateDiagram(this.topologyData)
    })
    this.lastValue.level = type;
    this.lastValue.type = this.topologyForm.get('type')?.value.toLowerCase();
  }
  get app() {
    return this.appForm.get('app')
  }
  get sender() {
    return this.appSettingsForm.get('sender')
  }
  get receiver() {
    return this.appSettingsForm.get('receiver')
  }
  get node1() {
    return this.appSettingsForm.get('endnode1')
  }
  get node2() {
    return this.appSettingsForm.get('endnode2')
  }
  get node3() {
    return this.appSettingsForm.get('endnode3')
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

}
function evenLengthValidator(control: FormControl) {
  const value = control.value;
  if (value.length % 2 !== 0) {
    return { evenLength: true };
  }
  return null;
}
function lengthValidator(control: FormControl) {
  const value = control.value;
  if (value.length <= 10 || value.length >= 8) {
    return { len: true };
  }
  return null
}




