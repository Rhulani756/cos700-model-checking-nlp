"use client";

import { X, FileCode2 } from "lucide-react";
import { COLORS } from "./colors";

export default function UploadInfo({
  selectedFiles,
  removeFile,
  clearAllFiles,
  compilationMode,
  setCompilationMode,
  handleUpload,
}) {
  return (
    <div className="lg:col-span-2">
      <div className="rounded-xl border overflow-hidden" style={{ borderColor: COLORS.gold, backgroundColor: COLORS.white }}>
        <div
          className="flex items-center justify-between px-4 py-3 border-b"
          style={{ borderColor: COLORS.goldLight, backgroundColor: COLORS.goldLight + "60" }}
        >
          <p className="text-sm font-semibold" style={{ color: COLORS.black }}>
            {selectedFiles.length} file{selectedFiles.length !== 1 ? "s" : ""} ready to upload
          </p>
          <button
            type="button"
            onClick={clearAllFiles}
            className="text-xs font-medium hover:opacity-80"
            style={{ color: COLORS.red }}
          >
            Clear all
          </button>
        </div>

        <div className="max-h-96 overflow-y-auto divide-y" style={{ borderColor: COLORS.goldLight }}>
          {selectedFiles.map((file, index) => (
            <div
              key={`${file.webkitRelativePath || file.name}-${index}`}
              className="flex items-center gap-2 px-4 py-2 text-sm"
              style={{ borderColor: COLORS.goldLight }}
            >
              <FileCode2 className="w-4 h-4 shrink-0" style={{ color: COLORS.gold }} />
              <span className="flex-1 truncate" style={{ color: COLORS.black }}>
                {file.webkitRelativePath || file.name}
              </span>
              <button
                type="button"
                onClick={() => removeFile(index)}
                aria-label={`Remove ${file.name}`}
                className="p-1 rounded-md hover:opacity-80"
                style={{ color: COLORS.red }}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>

        <div className="pr-3 pl-3 flex flex-col gap-2">
          <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: COLORS.black }}>
            Submission Type
          </p>
          <div
            className="flex gap-2 p-1 rounded-lg border"
            style={{ borderColor: COLORS.gold, backgroundColor: COLORS.goldLight }}
          >
            <button
              type="button"
              onClick={() => setCompilationMode("independent")}
              className="flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              style={{
                backgroundColor: compilationMode === "independent" ? COLORS.gold : "transparent",
                color: compilationMode === "independent" ? COLORS.white : COLORS.gold,
              }}
            >
              Independent Exercises
            </button>
            <button
              type="button"
              onClick={() => setCompilationMode("combined")}
              className="flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors"
              style={{
                backgroundColor: compilationMode === "combined" ? COLORS.gold : "transparent",
                color: compilationMode === "combined" ? COLORS.white : COLORS.gold,
              }}
            >
              Single Program
            </button>
          </div>
          <p className="text-xs pb-3" style={{ color: COLORS.black + "99" }}>
            {compilationMode === "independent"
              ? "Each .cpp file is treated as a separate exercise."
              : "All files are compiled and verified together (e.g. main.cpp using vehicle.cpp)."}
          </p>
        </div>

        <div className="px-4 py-3 border-t" style={{ borderColor: COLORS.goldLight, backgroundColor: COLORS.goldLight + "60" }}>
          <button
            type="button"
            onClick={handleUpload}
            className="w-full px-4 py-2 rounded-lg text-white font-medium transition-colors"
            style={{ backgroundColor: COLORS.blue }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = COLORS.blueDark)}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = COLORS.blue)}
          >
            Upload & Generate Feedback
          </button>
        </div>
      </div>
    </div>
  );
}