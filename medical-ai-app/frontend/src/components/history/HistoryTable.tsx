import { Download, Eye } from "lucide-react";
import { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { Card, CardContent } from "@/components/ui/card";
import type { CaseItem } from "@/types/case";
import { assetUrl, formatDateTime } from "@/lib/utils";
import { StatusBadge } from "@/components/common/StatusBadge";

export function HistoryTable({ items }: { items: CaseItem[] }) {
  const columns = useMemo<ColumnDef<CaseItem>[]>(
    () => [
      {
        header: "Mã ca",
        accessorKey: "case_code",
        cell: ({ row }) => <div className="font-semibold text-slate-900">{row.original.case_code}</div>,
      },
      {
        header: "Bệnh nhân / ID",
        cell: ({ row }) => (
          <div>
            <div className="font-semibold text-slate-900">{row.original.patient_identifier}</div>
            <div className="text-slate-500">{row.original.patient_name}</div>
          </div>
        ),
      },
      {
        header: "Thời gian",
        cell: ({ row }) => <div>{formatDateTime(row.original.created_at)}</div>,
      },
      {
        header: "Kết quả",
        cell: ({ row }) => <div className="font-semibold text-slate-900">{row.original.latest_prediction?.predicted_label ?? "--"}</div>,
      },
      {
        header: "Độ tin cậy",
        cell: ({ row }) => (
          <span className="inline-flex rounded-full bg-blue-50 px-3 py-1 text-sm font-semibold text-brand-600">
            {row.original.latest_prediction?.confidence ? row.original.latest_prediction.confidence.toFixed(2) : "--"}
          </span>
        ),
      },
      {
        header: "Trạng thái",
        cell: ({ row }) => <StatusBadge status={row.original.status} />,
      },
      {
        header: "Hành động",
        cell: ({ row }) => {
          const artifacts = row.original.latest_prediction?.artifacts || {};
          const downloadUrl = assetUrl(
            artifacts.overlay_image || artifacts.gradcam_image || artifacts.detection_image || artifacts.mask_image,
          );
          return (
            <div className="flex items-center gap-4">
              <Link
                to={`/reports?caseId=${row.original.id}`}
                className="inline-flex items-center gap-2 font-semibold text-brand-500"
              >
                <Eye className="h-4 w-4" />
                Xem
              </Link>
              <a href={downloadUrl} className="inline-flex items-center gap-2 font-semibold text-brand-500" target="_blank" rel="noreferrer">
                <Download className="h-4 w-4" />
                Tải
              </a>
            </div>
          );
        },
      },
    ],
    [],
  );

  const table = useReactTable({
    data: items,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  return (
    <Card>
      <CardContent className="pt-4">
        <div className="overflow-hidden rounded-[22px] border border-slate-200">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              {table.getHeaderGroups().map((headerGroup) => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map((header) => (
                    <th key={header.id} className="px-4 py-4 font-medium">
                      {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody>
              {table.getRowModel().rows.map((row) => (
                <tr key={row.id} className="border-t border-slate-200">
                  {row.getVisibleCells().map((cell) => (
                    <td key={cell.id} className="px-4 py-4 align-middle text-slate-700">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}
