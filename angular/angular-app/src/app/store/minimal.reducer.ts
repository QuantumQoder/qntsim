import { createReducer, on } from "@ngrx/store";
import {
  updateAppForm,
  updateAppSettingsForm,
  updateDebugOptions,
  updateEndNodes,
  updateServicesNodes,
  updateTopology,
  updateTopologyData,
  updateTopologyForm,
} from "./minimal.actions";
const moduleOptions = [
  {
    name: "NETWORK",
    value: "network",
  },
  {
    name: "PHYSICAL",
    value: "physical",
  },
  {
    name: "LINK",
    value: "link",
  },
  {
    name: "TRANSPORT",
    value: "transport",
  },

  {
    name: "APPLICATION",
    value: "application",
  },
  {
    name: "EVENT SIMULATION",
    value: "eventSimulation",
  },
];
const loggingLevelOptions = [
  {
    name: "DEBUG",
    value: "debug",
  },
  {
    name: "INFO",
    value: "info",
  },
];
const initialState = {
  appForm: "",
  appSettingsForm: "",
  topology: "",
  topologyForm: "",
  endNodes: [],
  servicesNodes: [],
  debugOptions: {
    moduleOptions: moduleOptions,
    loggingLevelOptions: loggingLevelOptions,
  },
  topologyData: "",
};

export const minimalReducer = createReducer(
  initialState,
  on(updateAppForm, (state, appForm: any) => ({ ...state, appForm })),
  on(updateAppSettingsForm, (state, appSettingsForm: any) => ({
    ...state,
    appSettingsForm,
  })),
  on(updateDebugOptions, (state, debugOptions: any) => ({
    ...state,
    debugOptions,
  })),
  on(updateTopology, (state, topology: any) => ({ ...state, topology })),
  on(updateTopologyForm, (state, topologyForm: any) => ({
    ...state,
    topologyForm,
  })),
  on(updateEndNodes, (state, endNodes: any) => ({ ...state, endNodes })),
  on(updateServicesNodes, (state, servicesNodes: any) => ({
    ...state,
    servicesNodes,
  })),
  on(updateTopologyData, (state, topologyData: any) => ({
    ...state,
    topologyData,
  }))
);
