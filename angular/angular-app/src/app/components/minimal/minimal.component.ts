import { CookieService } from 'ngx-cookie-service';
import { ApiServiceService } from './../../../services/api-service.service';

import { AfterViewInit, Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import * as go from 'gojs'
import { map } from 'rxjs';
import { ConditionsService } from 'src/services/conditions.service';
import { Router } from '@angular/router';
import { KatexOptions } from 'ng-katex';

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
  options: KatexOptions = {
    displayMode: true,
  };
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

  constructor(private fb: FormBuilder, private service: ConditionsService, private route: Router, private api: ApiServiceService, private cookie: CookieService) { }
  ngAfterViewInit(): void {
    let urlData = this.service.jsonUrl(this.topologyForm.get('type')?.value, this.level);
    this.service.getJson(urlData.url, urlData.type).subscribe((result) => {
      // console.log(result)
      this.topologyData = result;
      // console.log(this.topologyData.nodes)
    }, (error) => {
      console.log(error)
    }, () => {
      // console.log(this.topologyData.nodes)
      this.init(this.topologyData.nodes, this.topologyData.links)
    }
    )
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
      'noOfMemories': [100, Validators.required],
      'distance': [150, [Validators.required, Validators.max(150)]],
      'attenuity': [{ value: 0.00001, disabled: true }, Validators.required]
    });
    this.appForm = this.fb.group({
      'app': ['', Validators.required]
    });
    this.appSettingsForm = this.fb.group({
      'sender': [''],
      'receiver': [''],
      'targetFidelity': [0.5],
      'size': [6],
      'amplitude': [''],
      'endnode1': [''],
      'endnode2': [''],
      'endnode3': [''],
      'middleNode': ['']
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
  updateNodes() {
    this.nodes = this.topologyData.nodes
  }
  getType($event: any) {
    const { url, type } = this.service.jsonUrl(this.topologyForm.get('type')?.value.toLowerCase(), this.level);
    this.service.getJson(url, type).subscribe(
      (result: any) => {
        this.topologyData = result;
      },
      (error) => {
        console.log(error);
      },
      () => {
        this.updateDiagram(this.topologyData);
      }
    );
  }
  levelChange() {
    this.level = this.topologyForm.get('level')?.value;
    let urlData = this.service.jsonUrl(this.topologyForm.get('type')?.value.toLowerCase(), this.level);
    this.service.getJson(urlData.url, urlData.type).subscribe((result: any) => {
      this.topologyData = result;
      console.log(this.topologyData)
    }, (error) => {
      console.log(error)
    }, () => {
      this.updateDiagram(this.topologyData)
    })
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
        "undoManager.isEnabled": true  // enable undo & redo
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
    this.buildForm(this.appForm.get('app')?.value)
  }
  runApp() {
    this.spinner = true;
    var linkArray = []
    var nodeArray = []
    var linkRequestArray = []
    let nodeDataArray = this.topologyData.nodes
    let linkDataArray = this.topologyData.links
    this.service.setapp_id(this.appForm.get('app')?.value)
    for (var i = 0; i < nodeDataArray.length; i++) {
      var name = nodeDataArray[i].key;
      var type
      if (nodeDataArray[i].color == 'orange') {
        type = 'service'
      } else if (nodeDataArray[i].color == 'lightblue') {
        type = 'end'
      }
      var memory = this.service.getMemory();
      var noOfMemories = this.topologyForm.get('noOfMemories')?.value
      var singleNode = {
        Name: name,
        Type: type,
        noOfMemory: noOfMemories,
        memory: memory
      }
      nodeArray.push(singleNode)
    }
    console.log(nodeArray)
    for (var i = 0; i < linkDataArray.length; i++) {
      let from = linkDataArray[i].from
      let to = linkDataArray[i].to
      linkArray.push(from);
      linkArray.push(to);
      var linkData
      linkData = {
        Nodes: linkArray,
        Attenuation: this.topologyForm.get('attenuity')?.value,
        Distance: this.topologyForm.get('distance')?.value
      }
      linkArray = []
      linkRequestArray.push(linkData)
    }
    console.log(linkRequestArray);
    var cc = []
    for (var i = 0; i < nodeDataArray.length; i++) {
      for (var j = 0; j < nodeDataArray.length; j++) {
        cc.push([nodeDataArray[i].key, nodeDataArray[j].key]);
      }
    }
    if (cc.length != 0) {
      var distance
      var delay
      for (var i = 0; i < cc.length; i++) {
        if (cc[i][0] == cc[i][1]) {
          distance = 0;
          delay = 0;
        } else {
          distance = 1000;
          delay = 10000000000;
        }
        let ccreq = {
          Nodes: cc[i],
          Delay: delay,
          Distance: distance
        }
        this.cc.push(ccreq);
        console.log(this.cc)
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
    // this.appSettingsForm = null;

    switch (app) {
      case 1: this.appSettingsForm.addControl('keyLength', new FormControl());
        break;
      case 2: console.log(app)
        break;
      case 3: console.log(app);
        break;
      case 4: console.log(app);
        break;
      case 5: this.appSettingsForm.addControl('key', new FormControl());
        break;
      case 6: this.appSettingsForm.addControl('message', new FormControl());
        break;
      case 7: this.appSettingsForm.addControl('message', new FormControl());
        break;
      case 8: this.appSettingsForm.addControl('message1', new FormControl());
        this.appSettingsForm.addControl('message2', new FormControl());
        break;
      case 9: this.appSettingsForm.addControl('message', new FormControl());
        break;
      case 10: this.appSettingsForm.addControl('inputMessage', new FormControl());
        break;
    }
  }
  selectSender($event: any) {
    console.log(this.appSettingsForm.get('sender')?.value);
  }
  selectReceiver($event: any) {
    console.log(this.appSettingsForm.get('receiver')?.value)
  }
  getAppSettingsResults() {
    this.service.getAppSetting().subscribe((results: any) => {
      this.appSettingsResult = results
      // console.log("APP SETTINGS:" + this.appSettingsResult)
    })
  }
  getAppSetting(app_id: any) {

    switch (app_id) {
      case 2: this.appConfig = {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        startTime: 1e12,
        size: this.appSettingsForm.get('size')?.value,
        priority: 0,
        targetFidelity: this.appSettingsForm.get('targetFidelity')?.value,
        timeout: 2e12
      }
        // console.log(this.appConfig)
        break;
      case 1: this.appConfig = {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        keyLength: String(this.appSettingsForm.get('keyLength')?.value)
      }
        break;
      case 3: this.appConfig = {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        amplitude1: '0.70710678118+0j',
        amplitude2: '0-0.70710678118j'
      }
        break;
      case 4: this.appConfig = {
        endnode1: this.appSettingsForm.get('endnode1')?.value,
        endnode2: this.appSettingsForm.get('endnode2')?.value,
        endnode3: this.appSettingsForm.get('endnode3')?.value,
        middlenode: this.appSettingsForm.get('middleNode')?.value
      }
        break;
      case 5: this.appConfig = {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        sequenceLength: 3,
        key: this.appSettingsForm.get('key')?.value
      }
        break;
      case 6: this.appConfig = {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        sequenceLength: 2,
        message: this.appSettingsForm.get('message')?.value
      }
        break;
      case 7: this.appConfig = {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        message: this.appSettingsForm.get('message')?.value
      }
        break;
      case 8: this.appConfig = {
        sender: this.appSettingsForm.get('sender')?.value,
        receiver: this.appSettingsForm.get('receiver')?.value,
        message1: this.appSettingsForm.get('message1')?.value,
        message2: this.appSettingsForm.get('message2')?.value,
        num_photons: 5,
        attack: 'DoS'
      }
        break;
      case 9: this.appConfig = {
        sender: 1,
        receiver: 2,
        message: this.appSettingsForm.get('message')?.value,
        attack: 'None'
      }
        break;
      case 10:
        this.appConfig = { "input_messages": { "2": this.appSettingsForm.get('message')?.value, }, "ids": { "2": "1011", "1": "0111" }, "num_check_bits": 4, "num_decoy": 4 }
        break;
    }
  }

}




