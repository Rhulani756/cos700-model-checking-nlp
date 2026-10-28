"use client";

import { Upload, AlertTriangle, X, CheckCircle } from "lucide-react";
import { COLORS } from "./colors";

export default function UploadBox({
  showRightPanel,
  error,
  setError,
  uploadedFiles,
  fileInputRef,
  folderInputRef,
  handleFileUpload,
}) {
  return (
    <div
      className={`w-full transition-all duration-500 ${
        showRightPanel ? "lg:col-span-1" : "max-w-2xl"
      }`}
    >
      <div className="space-y-6">
        <h2 className="text-xl font-bold text-center" style={{ color: COLORS.black }}>
          Generate Feedback
        </h2>

        <div
          className="flex gap-2 p-1 rounded-lg border font-medium justify-center"
          style={{ backgroundColor: COLORS.blueLight, borderColor: COLORS.blue, color: COLORS.blueDark }}
        >
          Upload Assignment Code
        </div>

        {error && (
          <div className="fixed top-6 right-6 z-50">
            <div
              className="flex items-start gap-3 min-w-[320px] max-w-md p-4 rounded-xl border backdrop-blur-md shadow-2xl"
              style={{ backgroundColor: COLORS.black, borderColor: COLORS.red }}
            >
              <AlertTriangle className="w-5 h-5 mt-0.5" style={{ color: COLORS.red }} />
              <div className="flex-1">
                <p className="text-sm font-semibold" style={{ color: COLORS.red }}>Error</p>
                <p className="text-sm text-white/90 mt-1">{error}</p>
              </div>
              <button onClick={() => setError(null)}>
                <X className="w-4 h-4" style={{ color: COLORS.red }} />
              </button>
            </div>
          </div>
        )}

        <div className="space-y-4">
          <div
            className="border-2 border-dashed rounded-xl p-8 text-center"
            style={{ borderColor: COLORS.gold, backgroundColor: COLORS.goldLight + "40" }}
          >
            <Upload className="w-10 h-10 mx-auto mb-3" style={{ color: COLORS.gold }} />
            <p className="text-sm font-medium mb-4" style={{ color: COLORS.black }}>
              Upload C++ Files or an Entire Folder
            </p>
            <div className="flex justify-center gap-4">
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="px-4 py-2 rounded-lg text-white font-medium transition-colors"
                style={{ backgroundColor: COLORS.blue }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = COLORS.blueDark)}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = COLORS.blue)}
              >
                Select Files
              </button>
              <button
                type="button"
                onClick={() => folderInputRef.current?.click()}
                className="px-4 py-2 rounded-lg border font-medium transition-colors"
                style={{ borderColor: COLORS.black, color: COLORS.black }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = COLORS.goldLight)}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "transparent")}
              >
                Select Folder
              </button>
            </div>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".cpp,.h"
            className="hidden"
            onChange={handleFileUpload}
          />
          <input
            ref={folderInputRef}
            type="file"
            multiple
            webkitdirectory=""
            className="hidden"
            onChange={handleFileUpload}
          />

          {uploadedFiles.length > 0 && (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              <p className="text-xs font-semibold uppercase tracking-wide" style={{ color: COLORS.black }}>
                Uploaded
              </p>
              {uploadedFiles.map((file, index) => (
                <div
                  key={`${file.webkitRelativePath || file.name}-${index}`}
                  className="flex items-center gap-2 text-sm"
                  style={{ color: COLORS.blueDark }}
                >
                  <CheckCircle className="w-4 h-4 shrink-0" style={{ color: COLORS.blue }} />
                  <span className="truncate">{file.webkitRelativePath || file.name}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}