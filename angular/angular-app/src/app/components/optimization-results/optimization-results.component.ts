import { AfterViewChecked, AfterViewInit, Component, OnInit, ViewChild } from "@angular/core";
import {
  ChartComponent,
  ApexAxisChartSeries,
  ApexChart,
  ApexXAxis,
  ApexDataLabels,
  ApexTitleSubtitle,
  ApexStroke,
  ApexGrid,
  ApexYAxis
} from "ng-apexcharts";
import { OptimizationService } from "src/app/services/optimization.service";

export type ChartOptions = {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  xaxis: ApexXAxis;
  dataLabels: ApexDataLabels;
  grid: ApexGrid;
  stroke: ApexStroke;
  title: ApexTitleSubtitle;
  yaxis: ApexYAxis;
};
@Component({
  selector: 'app-optimization-results',
  templateUrl: './optimization-results.component.html',
  styleUrls: ['./optimization-results.component.less']
})
export class OptimizationResultsComponent implements OnInit {

  @ViewChild("chart") chart: ChartComponent;
  public chartOptions: Partial<ChartOptions>;
  results
  values = []
  constructor(private service: OptimizationService) { }

  ngOnInit(): void {
    this.service.currentResults.subscribe((data) => {
      console.log("Behavioral Subject", data)
      this.results = data;
      this.chartOptions = {
        series: [
          {
            name: "Cost per Iteration",
            data: data.graph
          }
        ],
        chart: {
          height: 500,
          type: "line",
          zoom: {
            enabled: false
          }
        },
        dataLabels: {
          enabled: false
        },
        stroke: {
          curve: "straight"
        },
        title: {
          text: "Cost Minimization Graph",
          align: "center"
        },
        grid: {
          row: {
            colors: ["#f3f3f3", "transparent"], // takes an array which will be repeated on columns
            opacity: 0.5
          }
        },
        xaxis: {
          title: {
            text: "Number of iterations",
          },
          labels: {
            show: true
          },
          categories: [

          ]
        },
        yaxis: {
          title: {
            text: 'Cost Value' // Label for y-axis
          }
        },
      };
      console.log("Behavioral Subject", data)

      this.values = this.formatOptimizedValues(data)
    })
  }


  formatOptimizedValues(values) {
    console.log("Inside the format function", values)
    const result = []

    for (let i = 0; i < values.initial_params.length; i++) {
      result.push({ initial: values.initial_params[i], final: values.initial_params[i] });
    }

    console.log("Result", result)
    return result
  }







}
