import { AfterViewInit, Component, OnInit } from '@angular/core';
import { FormBuilder, Validators } from '@angular/forms';
import * as go from 'gojs'
import { ConditionsService } from 'src/services/conditions.service';

@Component({
  selector: 'app-minimal',
  templateUrl: './minimal.component.html',
  styleUrls: ['./minimal.component.less']
})

export class MinimalComponent implements OnInit, AfterViewInit {
  topology: any
  topologyData: any
  levelChange() {
    this.level = this.minimalform.get('level')?.value;
    let urlData = this.service.jsonUrl(this.minimalform.get('type')?.value.toLowerCase(), this.level);
    this.service.getJson(urlData.url, urlData.type).subscribe((result: any) => {
      this.topologyData = result;
      console.log(this.topologyData)
    }, (error) => {
      console.log(error)
    }, () => {
      this.updateDiagram(this.topologyData)
    })
  }
  minimalform: any
  type = ['Star', 'Mesh'];
  level: number = 0
  constructor(private fb: FormBuilder, private service: ConditionsService) { }
  ngAfterViewInit(): void {
    let urlData = this.service.jsonUrl(this.minimalform.get('type')?.value, this.level);
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
  ngOnInit(): void {
    this.minimalform = this.fb.group({
      'type': ['Star', Validators.required],
      'level': [0, Validators.required]
    });

  }
  updateDiagram(data: any) {
    this.topology.model = new go.GraphLinksModel(
      data.nodes, data.links
    )
    console.log(this.topology.model.nodeDataArray);
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
        //    {
        //   routing: go.Link.AvoidsNodes,
        //   curve: go.Link.JumpOver
        // },
        // the whole link panel
        $(go.Shape),
        // $(go.Shape,   // the "from" end arrowhead
        //   { fromArrow: "Standard" }),
        // $(go.Shape,   // the "to" end arrowhead
        //   { toArrow: "Standard" })  // the link shape, default black stroke
      );
    this.topology.model = new go.GraphLinksModel(
      nodes, links
    )
  }
}






