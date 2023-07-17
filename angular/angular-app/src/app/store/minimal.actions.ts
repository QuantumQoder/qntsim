import { createAction, props } from "@ngrx/store";

export const updateAppForm = createAction(
  "[Minimal] Update App Form",
  props<any>()
);
export const updateAppSettingsForm = createAction(
  "[Minimal] Update App Settings Form",
  props<any>()
);
export const updateTopology = createAction(
  "[Minimal] Update Topology",
  props<any>()
);
export const updateTopologyForm = createAction(
  "[Minimal] Update Topology Form",
  props<any>()
);
export const updateEndNodes = createAction(
  "[Minimal] Update End Nodes",
  props<any>()
);
export const updateServicesNodes = createAction(
  "[Minimal] Update Services Nodes",
  props<any>()
);
export const updateDebugOptions = createAction(
  "[Minimal] Update Debug Options",
  props<any>()
);
export const updateTopologyData = createAction(
  "[Minimal] Update Topology Data",
  props<any>()
);
