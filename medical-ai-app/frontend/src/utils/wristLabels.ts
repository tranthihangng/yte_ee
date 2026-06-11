const WRIST_LABEL_VI: Record<string, string> = {
  "bone anomaly": "Bất thường xương",
  "bone lesion": "Tổn thương xương",
  "foreign body": "Dị vật",
  fracture: "Gãy xương",
  metal: "Vật liệu kim loại",
  "periosteal reaction": "Phản ứng màng xương",
  "pronator sign": "Dấu hiệu pronator quadratus",
  "soft tissue": "Tổn thương mô mềm",
  text: "Ký tự/nhãn chữ trên phim",
  normal: "Không ghi nhận bất thường rõ"
};

const normalize = (value: string): string =>
  value
    .trim()
    .toLowerCase()
    .replace(/-/g, " ")
    .replace(/_/g, " ")
    .replace(/\s+/g, " ");

export const mapWristLabelToVietnamese = (rawLabel?: string | null): string => {
  if (!rawLabel) return "-";
  const normalized = normalize(rawLabel);
  return WRIST_LABEL_VI[normalized] || rawLabel;
};
