import { api } from "./api";

export const predictionService = {
  run: (modulePath: "brain-mri" | "histopath" | "wrist-xray" | "tuberculosis-counting", formData: FormData) =>
    api.post(`/predict/${modulePath}`, formData, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data)
};
