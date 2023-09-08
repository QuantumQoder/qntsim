import { Component, OnInit } from "@angular/core";
import { ApiServiceService } from "src/app/services/api-service.service";
import { QuantumcircuitService } from "../quantum-circuit/quantumcircuit.service";

@Component({
  selector: "app-optimization",
  templateUrl: "./optimization.component.html",
  styleUrls: ["./optimization.component.less"],
})
export class OptimizationComponent implements OnInit {
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
  optimizationAlgos = {
    value: "",
    options: [],
  };
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

  constructor(
    private service: QuantumcircuitService,
    private apiService: ApiServiceService
  ) { }


  ngOnInit(): void {
    this.options = this.service.getGatesLocal();
    console.log(this.options);
    this.app_id = localStorage.getItem("app_id");
    this.requestData = this.apiService.getRequest();
    this.optimizationAlgos.value = this.service.getOptimizationAlogorithm();
    this.optimizationAlgos.options = this.service.getCircuitsForOptimization(
      this.service.getOptimizationAlogorithm()
    );
    console.log(this.optimizationAlgos);
    for (let node of this.optimizationAlgos.options) {
      this.tableData[node] = {
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
      this.tableData[node] = JSON.parse(JSON.stringify(this.tableData[node]));
    }
    console.log(this.tableData);
  }

  saveTableData() {
    console.log(
      "Save table data:",
      // this.tabOptions[this.tabActiveIndex].label,
      JSON.stringify(this.tableData)
    );

  }

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
      this.params.visible = true;
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
    this.apiService.optimization(this.optimizationAlgos.value, generatedCircuitData).subscribe({
      next: (res) => {
        console.log(res)
      }, error: (error) => {
        console.error(error)
      }, complete: () => {
        console.log("Completed!!")
      }
    })
    this.spinner = true;
    this.requestData.req["circuit"] = generatedCircuitData;
    this.generatedImage.presence = true;
    setTimeout(() => {
      this.spinner = false;
    }, 3000);


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
