import html2canvas from "html2canvas";
import jsPDF from "jspdf";

export const waitForAssetsReady = async (element: HTMLElement): Promise<void> => {
  if ("fonts" in document) {
    await (document as Document & { fonts: FontFaceSet }).fonts.ready;
  }
  const images = Array.from(element.querySelectorAll("img"));
  await Promise.all(
    images.map(
      (img) =>
        new Promise<void>((resolve) => {
          if (img.complete && img.naturalWidth > 0) {
            resolve();
            return;
          }
          img.addEventListener("load", () => resolve(), { once: true });
          img.addEventListener("error", () => resolve(), { once: true });
        })
    )
  );
};

export const captureElementAsCanvas = async (element: HTMLElement, scale = 3): Promise<HTMLCanvasElement> => {
  await waitForAssetsReady(element);
  return html2canvas(element, {
    scale,
    backgroundColor: "#ffffff",
    useCORS: true,
    allowTaint: false,
    imageTimeout: 30000
  });
};

export const generateReportPdfBlob = async (element: HTMLElement): Promise<Blob> => {
  const canvas = await captureElementAsCanvas(element, 3);
  const imgData = canvas.toDataURL("image/png", 1.0);
  const pdf = new jsPDF("p", "mm", "a4");
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();
  const margin = 10;
  const usableWidth = pageWidth - margin * 2;
  const imgHeight = (canvas.height * usableWidth) / canvas.width;
  const printableHeight = pageHeight - margin * 2;

  let remainingHeight = imgHeight;
  let offsetY = 0;
  while (remainingHeight > 0) {
    pdf.addImage(imgData, "PNG", margin, margin - offsetY, usableWidth, imgHeight, undefined, "SLOW");
    remainingHeight -= printableHeight;
    offsetY += printableHeight;
    if (remainingHeight > 0) {
      pdf.addPage();
    }
  }
  return pdf.output("blob");
};

export const printReportFromElement = async (element: HTMLElement): Promise<void> => {
  const canvas = await captureElementAsCanvas(element, 2.5);
  const imgData = canvas.toDataURL("image/png", 1.0);
  const printWindow = window.open("", "_blank", "width=900,height=1200");
  if (!printWindow) {
    throw new Error("PRINT_WINDOW_BLOCKED");
  }
  printWindow.document.write(`
    <html>
      <head>
        <title>In báo cáo</title>
        <style>
          @page { size: A4; margin: 10mm; }
          html, body { margin: 0; padding: 0; background: #fff; }
          body { display: flex; justify-content: center; }
          img { width: 190mm; height: auto; display: block; object-fit: contain; }
          * { -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }
        </style>
      </head>
      <body><img src="${imgData}" alt="Report preview"/></body>
    </html>
  `);
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 250);
};

export const fetchBlobByUrl = async (url: string): Promise<Blob> => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`FETCH_BLOB_FAILED_${response.status}`);
  }
  return response.blob();
};
