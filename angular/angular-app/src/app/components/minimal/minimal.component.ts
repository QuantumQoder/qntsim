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
  }
  minimalform: any
  type = ['Star', 'Mesh'];
  level: number = 0
  constructor(private fb: FormBuilder, private service: ConditionsService) { }
  ngAfterViewInit(): void {
    let urlData = this.service.jsonUrl('Mesh', 4);
    this.service.getJson(urlData.url, urlData.type).subscribe((result) => {
      // console.log(result)
      this.topologyData = result;
      // console.log(this.topologyData.nodes)
    }, (error) => {
      console.log(error)
    }, () => {
      // console.log(this.topologyData.nodes)
      init(this.topology, this.topologyData.nodes, this.topologyData.links)
    }
    )
    // this.level = 0

  }

  ngOnInit(): void {
    this.minimalform = this.fb.group({
      'type': ['Star', Validators.required],
      'level': [0, Validators.required]
    });

  }

}
function init(myDiagram: any, nodes: any, links: any) {

  var $ = go.GraphObject.make;  // for conciseness in defining templates

  myDiagram = $(go.Diagram, "topology",  // create a Diagram for the DIV HTML element
    {
      initialContentAlignment: go.Spot.Center,  // center the content
      "undoManager.isEnabled": true  // enable undo & redo
    });

  // define a simple Node template
  myDiagram.nodeTemplate =
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
  myDiagram.linkTemplate =
    $(go.Link, {
      routing: go.Link.AvoidsNodes
    },       // the whole link panel
      $(go.Shape),
      // $(go.Shape,   // the "from" end arrowhead
      //   { fromArrow: "Standard" }),
      // $(go.Shape,   // the "to" end arrowhead
      //   { toArrow: "Standard" })  // the link shape, default black stroke
    );
  myDiagram.model = new go.GraphLinksModel(
    nodes, links
  )
}



