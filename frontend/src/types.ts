export interface AppState {
  version?: string;
  runtime?: any;
  model?: any;
  memory_count?: number;
  state?: {
    uncertainty?: number;
    confidence?: number;
    energy?: number;
    workload?: number;
    attention_load?: number;
    task_pressure?: number;
  };
  safety?: {
    autonomy_level?: number;
    external_actions_require_approval?: boolean;
    local_only?: boolean;
    secret_remote_blocking?: boolean;
  };
  global_workspace_v2?: any;
  self_model_v2?: any;
  world_model?: any;
  goals?: any[];
  learning_v2?: any;
}
