import { result } from 'underscore';
import { AfterViewInit, Component, OnInit } from '@angular/core';
import { FormBuilder, FormControl, FormGroup, Validators } from '@angular/forms';
import * as go from 'gojs'
import { map } from 'rxjs';
import { ConditionsService } from 'src/services/conditions.service';

@Component({
  selector: 'app-minimal',
  templateUrl: './minimal.component.html',
  styleUrls: ['./minimal.component.less']
})

export class MinimalComponent implements OnInit, AfterViewInit {
  fields = []
  formData =
    [{
      "label": "sender"
    },
    {
      "label": "receiver"
    }]
  topology: any
  topologyData: any
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
  topologyForm: any
  appForm: any
  applist: any
  appSettingsForm: any
  type = ['Star', 'Mesh'];
  level: number = 0
  constructor(private fb: FormBuilder, private service: ConditionsService) { }
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
    for (let i = 0; i < formData.length; i++) {
      form[formData[i].formField] = new FormControl('')
    }
    this.appSettingsForm = new FormGroup(form)
  }
  ngOnInit(): void {
    this.topologyForm = this.fb.group({
      'type': ['Star', Validators.required],
      'level': [0, Validators.required],
      'noOfMemories': [100, Validators.required],
      'distance': [150, Validators.required],
      'attenuity': [0.98, Validators.required]
    });
    this.appForm = this.fb.group({
      'app': ['', Validators.required],

    })

    this.appSettingsForm = this.fb.group({
      'sender': ['', Validators.required],
      'receiver': ['', Validators.required]
    })
    this.service.getAppList().pipe(map((d: any) => d.appList)).subscribe((result: any) => this.applist = result);
  }
  updateDiagram(data: any) {
    this.topology.model = new go.GraphLinksModel(
      data.nodes, data.links
    )
    console.log(this.topology.model.nodeDataArray);
  }
  get() {
    console.log(this.appSettingsForm.get('sender')?.value)
    console.log(this.appSettingsForm.get('receiver')?.value)
    console.log(this.appSettingsForm.get('keyLength')?.value)
  }
  getType($event: any) {
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
  init(nodes: any, links: any) {
    var $ = go.GraphObject.make;  // for conciseness in defining templates
    this.topology = $(go.Diagram, "topology",  // create a Diagram for the DIV HTML element
      {
        initialContentAlignment: go.Spot.Center,  // center the content
        "undoManager.isEnabled": true  // enable undo & redo
      });
    // define a simple Node template
    this.topology.nodeTemplate =
      $(go.Node, "Auto",  // the Shape will go around the TextBlock
        $(go.Shape, "RoundedRectangle", { strokeWidth: 0 },
          // Shape.fill is bound to Node.data.color
          new go.Binding("fill", "color")),
        new go.Binding("location", "loc", go.Point.parse),

        $(go.TextBlock,
          { margin: 8 },  // some room around the text
          // TextBlock.text is bound to Node.data.key
          new go.Binding("text", "key"))
      );
    this.topology.linkTemplate =
      $(go.Link,
        $(go.Shape),
      );
    this.topology.model = new go.GraphLinksModel(
      nodes, links
    )
  }
  getApp($event: any) {
    console.log(this.appForm.get('app')?.value)
    let app = this.appForm.get('app')?.value
    this.service.getAppSetting($event.target.value).subscribe((result: any) => {

      console.log(result[app]);
      this.applist = result[app]
      console.log(result);
      this.setSettings(this.applist)
    })
  }
}






