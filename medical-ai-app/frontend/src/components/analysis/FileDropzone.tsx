import { UploadCloud } from "lucide-react";
import { useRef } from "react";
import { Button } from "@/components/ui/button";

export function FileDropzone({
  accept,
  onFileChange,
}: {
  accept: string;
  onFileChange: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  return (
    <div
      onDragOver={(event) => event.preventDefault()}
      onDrop={(event) => {
        event.preventDefault();
        const file = event.dataTransfer.files[0];
        if (file) onFileChange(file);
      }}
      className="rounded-[22px] border border-dashed border-blue-200 bg-blue-50/40 p-5 text-center"
    >
      <div className="flex flex-col items-center gap-3">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-white text-brand-500 shadow-soft">
          <UploadCloud className="h-5 w-5" />
        </div>
        <div className="text-sm leading-6 text-slate-600">
          Kéo & thả tệp vào đây
          <br />
          hoặc
        </div>
        <Button type="button" onClick={() => inputRef.current?.click()}>
          Chọn tệp
        </Button>
        <div className="text-xs text-slate-400">Định dạng hỗ trợ: {accept}</div>
      </div>
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        accept={accept}
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) onFileChange(file);
        }}
      />
    </div>
  );
}
