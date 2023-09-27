import { AfterViewInit, Component, OnDestroy, OnInit } from "@angular/core";
import { Router } from "@angular/router";
import { ApiServiceService } from "src/app/services/api-service.service";
import { CircuitResultsService } from "src/app/services/circuitresults.service";
import { QuantumcircuitService } from "src/app/services/quantumcircuit.service";
@Component({
  selector: "app-quantum-circuit",
  templateUrl: "./quantum-circuit.component.html",
  styleUrls: ["./quantum-circuit.component.less"],
})
export class QuantumCircuitComponent
  implements OnInit, OnDestroy, AfterViewInit {
  gatesParams = false;
  generatedImage = {
    presence: false,
    data: "b'UUlTS0lUBgAXAgAAAAAAAAABcQAKaQAIAAAAAgAAAAAAAAAAAAAABAAAAAEAAAAAAAAAAmNpcmN1aXQtOTAAAAAAAAAAAG51bGxxAQAAAAIAAQFxAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAUAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASEdhdGVxAAAAAAAGAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAAAABAAAAAUNYR2F0ZXEAAAAAcQAAAAEAAA=='",
  };
  circuitImage;
  params = {
    visible: false,
    value: {
      theta: { value: 0, variable: false },
      phi: { value: 0, variable: false },
      lambda: { value: 0, variable: false },
      // variable: false,
    },
  };
  circuitLayers = {
    visible: false,
    params: {
      numOfLayers: 2
    }
  }
  selectedCell = {
    nodeName: "",
    rowIndex: "",
    colIndex: "",
  };
  currentValue;
  subscription;
  rows = [0];
  cols = [0, 1];
  options = [];
  // tableData = [[null, null]];
  tableData: any = {};
  // tabOptions = [];
  tabActiveIndex = 1;
  requestData: any;
  app_id: string;
  tabActiveLabel;
  spinner: boolean;
  encodingOptions = [{ header: "State Encoding", value: 'state' }, { header: "Gate encoding", value: "gate" }]
  appParams: any = {}
  constructor(
    private service: QuantumcircuitService,
    private resultService: CircuitResultsService,
    private apiService: ApiServiceService, // private con: ConditionsService,
    private _route: Router
    // private fb: FormBuilder
  ) { }
  ngAfterViewInit(): void {
    // this.params.visible = true;
  }

  ngOnInit(): void {
    this.options = this.service.getGatesLocal();
    console.log(this.options);
    this.app_id = localStorage.getItem("app_id");
    this.requestData = this.apiService.getRequest();
    for (let node of this.requestData.req.topology.nodes) {
      this.tableData[node.Name] = {
        data: Array.from({ length: this.rows.length }, () =>
          Array(this.cols.length).fill({
            value: "I",
            params: {
              theta: { value: 0, variable: false },
              phi: { value: 0, variable: false },
              lambda: { value: 0, variable: false },
            },
          })
        ),
        rows: [...this.rows],
        cols: [...this.cols],
      };
      this.appParams[node.Name] = JSON.parse(JSON.stringify({ message: "", encoding: "" }))
      this.tableData[node.Name] = JSON.parse(
        JSON.stringify(this.tableData[node.Name])
      );
    }
    console.log(this.tableData);
    console.log(this.appParams)
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
  optionChanged(nodeName, rowIndex, colIndex) {
    if (
      this.tableData[nodeName].data[rowIndex][colIndex].value == "RX" ||
      this.tableData[nodeName].data[rowIndex][colIndex].value == "RY" ||
      this.tableData[nodeName].data[rowIndex][colIndex].value == "RZ" ||
      this.tableData[nodeName].data[rowIndex][colIndex].value == "U"
    ) {
      this.params.value.lambda =
        this.tableData[nodeName].data[rowIndex][colIndex].params.lambda;
      this.params.value.phi =
        this.tableData[nodeName].data[rowIndex][colIndex].params.phi;
      this.params.value.theta =
        this.tableData[nodeName].data[rowIndex][colIndex].params.theta;
      // this.params.value.variable.value =
      // this.tableData[nodeName].data[rowIndex][colIndex].params.variable;
      this.params.visible = true;
      // this.selectedCell.nodeName = nodeName;
      // this.selectedCell.rowIndex = rowIndex;
      // this.selectedCell.colIndex = colIndex;
      this.selectedCell = { nodeName, rowIndex, colIndex };
    }
    this.gatesParams =
      this.tableData[nodeName].data[rowIndex][colIndex].value == "U"
        ? true
        : false;
    console.log(this.tableData);
    return;
  }

  addRow(nodeName: string) {
    this.tableData[nodeName].rows.push(this.tableData[nodeName].rows.length);
    const newRow = new Array(this.tableData[nodeName].cols.length).fill({
      value: "I",
      params: {
        theta: { value: 0, variable: false },
        phi: { value: 0, variable: false },
        lambda: { value: 0, variable: false },
      },
    });
    this.tableData[nodeName].data.push(newRow);
    this.tableData = JSON.parse(JSON.stringify(this.tableData));
  }

  addColumn(nodeName: string) {
    this.tableData[nodeName].cols.push(this.tableData[nodeName].cols.length);
    this.tableData[nodeName].data.forEach((row) =>
      row.push({
        value: "I",
        params: {
          theta: { value: 0, variable: false },
          phi: { value: 0, variable: false },
          lambda: { value: 0, variable: false },
        },
      })
    );
    this.tableData = JSON.parse(JSON.stringify(this.tableData));
  }
  saveParams() {
    const { nodeName, rowIndex, colIndex } = this.selectedCell;
    this.tableData[nodeName].data[rowIndex][colIndex].params.theta.value =
      this.params.value.theta.value;
    this.tableData[nodeName].data[rowIndex][colIndex].params.theta.variable =
      this.params.value.theta.variable;
    this.tableData[nodeName].data[rowIndex][colIndex].params.lambda.value =
      this.params.value.lambda.value;
    this.tableData[nodeName].data[rowIndex][colIndex].params.lambda.variable =
      this.params.value.lambda.variable;
    this.tableData[nodeName].data[rowIndex][colIndex].params.phi.value =
      this.params.value.phi.value;
    this.tableData[nodeName].data[rowIndex][colIndex].params.phi.variable =
      this.params.value.phi.variable;
    // this.tableData[nodeName].data[rowIndex][colIndex].params.variable =
    //   this.params.value.variable;

    this.params.visible = false;
    this.gatesParams = false;
    console.log(JSON.stringify(this.tableData));
  }
  sendRequest() {
    const generatedCircuitData = this.generateRequestForCircuit(this.tableData);
    const topology = this.apiService.getRequest().req.topology
    const appParams = this.appParams
    // console.log(this.appParams)
    const requestPayload: any = { circuit: { ...generatedCircuitData }, topology, appParams }
    console.log("requestPayload from quantum-circuit", requestPayload)
    this.resultService.execute(requestPayload).subscribe({
      next: (res) => {
        console.log(res);
        this.resultService.setResults(res)
      },
      error: function (err) {
        console.error(err)
      },
      complete: () => {
        this._route.navigate(["circuit-results"])
      },
    })
    // this.apiService.execute(requestPayload).subscribe({
    //   next: (res) => {
    //     console.log(res)
    //     this.resultService.setResults(res);
    //   },
    //   error: function (err) {
    //     console.error(err)
    //   },
    //   complete: () => {
    //     this._route.navigate(["circuit-results"])
    //   }
    // })
    this.spinner = true;

    this.requestData.req["circuit"] = generatedCircuitData;

    this.generatedImage.presence = true;

    // this.apiService
    //   .advancedRunApplication(this.requestData.req, this.requestData.url)
    //   .subscribe({
    //     next: (response) => {
    //       this.con.setResult(response);

    //       if (response.application.Err_msg) {
    //         alert(`Error has occurred!! ${response.application.Err_msg}`);
    //       }
    //     },
    //     error: (error) => {
    //       console.error(`Error: ${error}`);
    //       // this.spinner = false;
    //       alert(
    //         `Error has occurred! Status Code:${error.status} Status Text:${error.statusText}`
    //       );
    //     },
    //     complete: () => {
    //       // this.spinner = false;
    //       // sessionStorage.setItem("saved_model", this.myDiagram.model);
    //       // this._route.navigate(["/results"]);
    //     },
    //   });
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
      transformedData[nodeName] = {};
      for (let i = 0; i < nodeRows.length; i++) {
        const rowData = nodeData[i].map((entry) => {
          if (entry.value === "U") {
            return {
              value: entry.value.toLowerCase(),
              params: entry.params,
            };
          } else if (
            entry.value === "RX" ||
            entry.value === "RY" ||
            entry.value === "RZ"
          ) {
            return {
              value: entry.value.toLowerCase(),
              params: {
                theta: entry.params.theta,
              },
            };
          } else {
            return {
              value: entry.value.toLowerCase(),
            };
          }
        });
        transformedData[nodeName]["q" + nodeRows[i]] = rowData;
      }
    }
    console.log(JSON.stringify(transformedData));
    return transformedData;
  }
}
