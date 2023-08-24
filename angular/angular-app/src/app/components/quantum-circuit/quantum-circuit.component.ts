import { Component, OnDestroy, OnInit } from "@angular/core";
// import { FormBuilder, FormGroup, FormArray, FormControl } from "@angular/forms";
// import { MatrixInputService } from "../matrix-input/matrix-input.service";
import { ApiServiceService } from "src/app/services/api-service.service";
import { ConditionsService } from "src/app/services/conditions.service";
import { Router } from "@angular/router";
import { QuantumcircuitService } from "./quantumcircuit.service";
@Component({
  selector: "app-quantum-circuit",
  templateUrl: "./quantum-circuit.component.html",
  styleUrls: ["./quantum-circuit.component.less"],
})
export class QuantumCircuitComponent implements OnInit, OnDestroy {
  circuitImage;
  currentValue;
  subscription;
  rows = [0];
  cols = [0, 1];
  options = [];
  // tableData = [[null, null]];
  tableData = {};
  // tabOptions = [];
  tabActiveIndex = 1;
  requestData: any;
  app_id: string;
  tabActiveLabel;
  spinner: boolean;

  constructor(
    private service: QuantumcircuitService,
    private apiService: ApiServiceService,
    private con: ConditionsService,
    private _route: Router // private fb: FormBuilder
  ) {}

  ngOnInit(): void {
    this.app_id = localStorage.getItem("app_id");
    this.requestData = this.apiService.getRequest();

    for (let node of this.requestData.req.topology.nodes) {
      this.tableData[node.Name] = {
        data: Array.from({ length: this.rows.length }, () =>
          Array(this.cols.length).fill("I")
        ),
        rows: [...this.rows],
        cols: [...this.cols],
      };
    }

    console.log(this.tableData);

    // this.tabOptions = this.requestData.req.topology.nodes.map((node, index) => {
    //   return {
    //     label: node.Name,
    //     command: () => this.updateActive({ index: index }),
    //   };
    // });

    // for (let node of this.requestData.req.topology.nodes) {
    //   this.service.updateTableData(node.Name, {
    //     data: this.tableData,
    //     rows: this.rows,
    //     cols: this.cols,
    //   });
    // }

    this.subscription = this.service.getGates().subscribe({
      next: (data: any) => {
        // console.log(data);
        this.options = data.map((current) => current.gate_name);
        console.log(this.options);
      },
      error: (error) => console.error(error),
    });

    // this.service.tableData$.subscribe((data: any) => {
    //   console.log("constructor" + JSON.stringify(data));
    //   // if (data[this.tabOptions[this.tabActiveIndex]["label"]] == undefined) {
    //   //   data[this.tabOptions[this.tabActiveIndex].label] = Array(
    //   //     this.rows.length
    //   //   ).fill(Array(this.cols.length).fill("I"));
    //   // } else {
    //   this.tableData = data[this.tabOptions[this.tabActiveIndex].label]["data"];
    //   this.rows = data[this.tabOptions[this.tabActiveIndex].label]["rows"];
    //   this.cols = data[this.tabOptions[this.tabActiveIndex].label]["cols"];
    //   console.log("Subscription", this.tableData, this.rows, this.cols);
    //   this.currentValue = data;

    // });
  }

  saveTableData() {
    console.log(
      "Save table data:",
      // this.tabOptions[this.tabActiveIndex].label,
      JSON.stringify(this.tableData)
    );
    // this.service.updateTableData(this.tabOptions[this.tabActiveIndex].label, {
    //   data: this.tableData,
    //   rows: this.rows,
    //   cols: this.cols,
    // });
  }

  // addRow(data) {
  //   this.rows.push(this.rows.length);
  //   console.log("addRow", this.tableData);
  //   this.tableData[data].push(new Array(this.cols.length).fill("I"));
  //   console.log("addRow", this.tableData);
  //   this.saveTableData();
  // }

  // addColumn(data) {
  //   this.cols.push(this.cols.length);
  //   console.log("addColumn", this.tableData);
  //   this.tableData[data].forEach((row) => row.push("I"));
  //   console.log("addColumn", this.tableData);
  //   this.saveTableData();
  // }

  addRow(nodeName: string) {
    this.tableData[nodeName].rows.push(this.tableData[nodeName].rows.length);
    const newRow = new Array(this.tableData[nodeName].cols.length).fill("I");
    this.tableData[nodeName].data.push(newRow);
  }

  addColumn(nodeName: string) {
    this.tableData[nodeName].cols.push(this.tableData[nodeName].cols.length);
    this.tableData[nodeName].data.forEach((row) => row.push("I"));
  }

  sendRequest() {
    const generatedCircuitData = this.generateRequestForCircuit(this.tableData);

    this.spinner = true;

    this.requestData.req["circuit"] = generatedCircuitData;
    this.apiService
      .advancedRunApplication(this.requestData.req, this.requestData.url)
      .subscribe({
        next: (response) => {
          this.con.setResult(response);

          if (response.application.Err_msg) {
            alert(`Error has occurred!! ${response.application.Err_msg}`);
          }
        },
        error: (error) => {
          console.error(`Error: ${error}`);
          // this.spinner = false;
          alert(
            `Error has occurred! Status Code:${error.status} Status Text:${error.statusText}`
          );
        },
        complete: () => {
          // this.spinner = false;
          // sessionStorage.setItem("saved_model", this.myDiagram.model);
          // this._route.navigate(["/results"]);
        },
      });
  }

  // updateActive(event) {
  //   // console.log(event);
  //   this.tabActiveIndex = event.index;

  //   // this.saveTableData();
  //   console.log();
  //   this.tableData = this.currentValue[this.tabOptions[event.index].label];
  //   console.log(this.options, this.currentValue, this.rows, this.cols);
  //   // this.tableData = this.service.tableDataSubject.getValue()[this.tabOptions[event.index]];
  // }

  ngOnDestroy(): void {
    // this.subscription.unsubscribe();
  }

  generateRequestForCircuit(inputData) {
    const transformedData = {};

    for (const nodeName in inputData) {
      const nodeData = inputData[nodeName].data;
      const nodeRows = inputData[nodeName].rows;
      // const nodeCols = inputData[nodeName].cols;

      transformedData[nodeName] = {};

      for (let i = 0; i < nodeRows.length; i++) {
        transformedData[nodeName]["q" + nodeRows[i]] = nodeData[i].map(
          (value) => value.toLowerCase()
        );
      }
    }

    console.log(transformedData);

    return transformedData;
  }
}
