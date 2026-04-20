import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Pagination({
  page,
  total,
  pageSize,
  onPageChange,
}: {
  page: number;
  total: number;
  pageSize: number;
  onPageChange: (page: number) => void;
}) {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="flex items-center justify-between gap-4">
      <div className="text-sm text-slate-500">
        Hiển thị {Math.min((page - 1) * pageSize + 1, total)} - {Math.min(page * pageSize, total)} / {total} ca
      </div>
      <div className="flex items-center gap-2">
        <Button size="icon" variant="outline" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
          <ChevronLeft className="h-4 w-4" />
        </Button>
        {Array.from({ length: Math.min(totalPages, 5) }, (_, index) => {
          const pageNumber = index + 1;
          return (
            <Button
              key={pageNumber}
              size="sm"
              variant={page === pageNumber ? "default" : "outline"}
              onClick={() => onPageChange(pageNumber)}
            >
              {pageNumber}
            </Button>
          );
        })}
        <Button size="icon" variant="outline" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
