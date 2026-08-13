"use client";

import Link from "next/link"
import { useState, useEffect, useRef } from "react"
import {
  Upload,
  AlertTriangle,
  X,
  CheckCircle,
  FileCode2
} from "lucide-react";

const PANEL = {
  NONE: "none",
  STAGING: "staging",
  RESULTS: "results",
};

// Palette - University of Pretoria badge
const COLORS = {
  red: "#C8102E",
  redDark: "#9E0C24",
  gold: "#C6963C",
  goldLight: "#F3E6C8",
  blue: "#1B4C96",
  blueDark: "#123869",
  blueLight: "#E4ECF8",
  black: "#0A0A0A",
  white: "#FFFFFF",
};

function FeedbackSection({ title, children }) {
  return (
    <div>
      <p
        className="text-xs font-semibold uppercase tracking-wide mb-2"
        style={{ color: COLORS.blueDark }}
      >
        {title}
      </p>
      {children}
    </div>
  );
}

export default function Home() {
  const [selectedFiles, setselectedFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [panelMode, setPanelMode] = useState(PANEL.NONE);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [Assignments, setAssignments] = useState([]);
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);
  const [compilationMode, setCompilationMode] = useState("independent");

  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(null), 7000);
    return () => clearTimeout(timer);
  }, [error]);

  const ALLOWED_EXTENSIONS = [".cpp", ".h"];

  const hasAllowedExtension = (filename) =>
    ALLOWED_EXTENSIONS.some((ext) => filename.toLowerCase().endsWith(ext));

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files).filter((f) =>
      hasAllowedExtension(f.name)
    );

    setselectedFiles((prev) => {
      const existingKeys = new Set(
        prev.map((f) => f.webkitRelativePath || f.name)
      );
      const newOnes = files.filter(
        (f) => !existingKeys.has(f.webkitRelativePath || f.name)
      );
      return [...prev, ...newOnes];
    });

    setPanelMode(PANEL.STAGING);

    e.target.value = "";
  };

  const removeFile = (indexToRemove) => {
    setselectedFiles((prev) => {
      const next = prev.filter((_, i) => i !== indexToRemove);
      if (next.length === 0) setPanelMode(PANEL.NONE);
      return next;
    });
  };

  const clearAllFiles = async () => {
    setselectedFiles([]);
    setPanelMode(PANEL.NONE);
    try {
      // delete
      const uploadRes = await fetch("http://localhost:8000/api/delete", {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) {
        const errBody = await uploadRes.json().catch(() => ({}));
        throw new Error(
          errBody.detail ||
          `Delete failed with status ${uploadRes.status}`
        );
      }

    } catch (err) {
      setError(err.message || "Delete failed. Please try again.");
      setPanelMode(PANEL.NONE);
    } finally {
      setLoading(false);
    }
  };

  const closePanel = () => {
    if (panelMode === PANEL.STAGING) {
      setselectedFiles([]);
    }
    setUploadedFiles([]);
    setAssignments([]);
    setPanelMode(PANEL.NONE);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError("Select at least one file before uploading.");
      return;
    }

    setUploadedFiles(selectedFiles);
    setselectedFiles([]);
    setPanelMode(PANEL.RESULTS);
    setLoading(true);
    setAssignments([]);

    const formData = new FormData();

    selectedFiles.forEach((file) => {
      formData.append("files", file);
      formData.append(
        "relative_paths",
        file.webkitRelativePath || file.name
      );
    });

    try {
      // Upload
      const uploadRes = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadRes.ok) {
        const errBody = await uploadRes.json().catch(() => ({}));
        throw new Error(
          errBody.detail ||
          `Upload failed with status ${uploadRes.status}`
        );
      }

      // Upload succeeded
      const uploadData = await uploadRes.json();
      console.log(uploadData);

      // Generate feedback
      const feedbackRes = await fetch("http://localhost:8000/api/feedback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ submission_id: uploadData.submission_id, compilation_mode: compilationMode, }),
      });

      if (!feedbackRes.ok) {
        const errBody = await feedbackRes.json().catch(() => ({}));
        throw new Error(
          errBody.detail ||
          `Feedback generation failed with status ${feedbackRes.status}`
        );
      }

      const feedback = await feedbackRes.json();
      console.log(feedback);

      setAssignments([feedback]);

    } catch (err) {
      setError(err.message || "Upload failed. Please try again.");
      setPanelMode(PANEL.NONE);
    } finally {
      setLoading(false);
    }
  };

  const showRightPanel = panelMode !== PANEL.NONE;

  return (
    <div className="flex-1 min-h-0 flex flex-col bg-white font-sans">

      <header className="border-b-4" style={{ backgroundColor: COLORS.black, borderColor: COLORS.gold }}>
        <div className="px-12 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-black tracking-tight text-white">
                Model Checking and NLP to Provide Pedagogic Feedback
              </h1>
              <p className="text-sm font-medium tracking-wide" style={{ color: COLORS.gold }}>
                Research Prototype
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center max-w-7xl mx-auto px-6 py-12 w-full">
        <div
          className={`grid gap-8 w-full transition-all duration-500 ${showRightPanel
            ? "grid-cols-1 lg:grid-cols-3"
            : "grid-cols-1 place-items-center"
            }`}
        >
          {/* Left Panel */}
          <div
            className={`w-full transition-all duration-500 ${showRightPanel ? "lg:col-span-1" : "max-w-2xl"
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

              {/* Error */}
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

              {/* Upload */}
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

                {/* File */}
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept=".cpp,.h"
                  className="hidden"
                  onChange={handleFileUpload}
                />

                {/* Folder */}
                <input
                  ref={folderInputRef}
                  type="file"
                  multiple
                  webkitdirectory=""
                  className="hidden"
                  onChange={handleFileUpload}
                />

                {/* Confirmed files */}
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
                        <span className="truncate">
                          {file.webkitRelativePath || file.name}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Panel */}
          {showRightPanel && (
            <div className="lg:col-span-2">
              <div className="rounded-xl border overflow-hidden" style={{ borderColor: COLORS.gold, backgroundColor: COLORS.white }}>
                <div
                  className="flex items-center justify-between px-4 py-3 border-b"
                  style={{ borderColor: COLORS.goldLight, backgroundColor: COLORS.goldLight + "60" }}
                >
                  <p className="text-sm font-semibold" style={{ color: COLORS.black }}>
                    {panelMode === PANEL.STAGING
                      ? `${selectedFiles.length} file${selectedFiles.length !== 1 ? "s" : ""} ready to upload`
                      : "Feedback"}
                  </p>

                  <div className="flex items-center gap-3">
                    {panelMode === PANEL.STAGING && (
                      <button
                        type="button"
                        onClick={clearAllFiles}
                        className="text-xs font-medium hover:opacity-80"
                        style={{ color: COLORS.red }}
                      >
                        Clear all
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={closePanel}
                      aria-label="Close panel"
                      className="p-1 rounded-md hover:opacity-80"
                      style={{ color: COLORS.black }}
                    >
                      <X className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {panelMode === PANEL.STAGING && (
                  <>
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
                  </>
                )}

                {panelMode === PANEL.RESULTS && (
                  loading ? (
                    <div className="h-96 flex flex-col items-center justify-center">
                      <div
                        className="w-12 h-12 rounded-full border-4 animate-spin mb-4"
                        style={{ borderColor: COLORS.goldLight, borderTopColor: COLORS.blue }}
                      />
                      <p style={{ color: COLORS.black }}>Generating Feedback...</p>
                    </div>
                  ) : Assignments.length === 0 ? (
                    <div className="h-96 flex items-center justify-center">
                      <p style={{ color: COLORS.black }}>Error Uploading Files. Please try again.</p>
                    </div>
                  ) : (
                    <div className="space-y-8 p-4">
                      {Assignments.map((result, idx) => {
                        const passed = result.verification_status !== "FAILED";
                        const fb = result.feedback;

                        return (
                          <div key={idx} className="space-y-6">
                            {/* File + verdict header */}
                            <div
                              className="flex items-center gap-3 p-4 rounded-xl border"
                              style={{
                                borderColor: passed ? COLORS.blue : COLORS.red,
                                backgroundColor: passed ? COLORS.blueLight : COLORS.redDark + "10",
                              }}
                            >
                              {passed ? (
                                <CheckCircle className="w-6 h-6 shrink-0" style={{ color: COLORS.blue }} />
                              ) : (
                                <AlertTriangle className="w-6 h-6 shrink-0" style={{ color: COLORS.red }} />
                              )}
                              <div className="min-w-0">
                                <p className="text-sm font-semibold truncate" style={{ color: COLORS.black }}>
                                  {result.file}
                                </p>
                                <p className="text-xs" style={{ color: passed ? COLORS.blueDark : COLORS.red }}>
                                  {passed
                                    ? "Verification passed"
                                    : `Verification failed${result.line ? ` at line ${result.line}` : ""}`}
                                </p>
                              </div>
                            </div>

                            {/* Other files in the submission that weren't shown */}
                            {result.other_files && result.other_files.length > 0 && (
                              <p className="text-xs" style={{ color: COLORS.black + "99" }}>
                                {result.other_files.length} other file
                                {result.other_files.length !== 1 ? "s" : ""} in this submission not shown:{" "}
                                {result.other_files.join(", ")}
                              </p>
                            )}

                            {passed && (
                              <p className="text-sm" style={{ color: COLORS.black }}>
                                No violations were detected in this file.
                              </p>
                            )}

                            {!passed && fb && (
                              <>
                                {/* Title + summary */}
                                <div>
                                  <h3 className="text-lg font-bold" style={{ color: COLORS.black }}>
                                    {fb.title}
                                  </h3>
                                  <p className="text-sm mt-1" style={{ color: COLORS.blueDark }}>
                                    {fb.summary}
                                  </p>
                                </div>

                                {/* Root cause */}
                                <FeedbackSection title="Root Cause">
                                  <p className="text-sm" style={{ color: COLORS.black }}>{fb.root_cause}</p>
                                </FeedbackSection>

                                {/* Evidence */}
                                <FeedbackSection title="Evidence">
                                  <ul className="list-disc list-inside space-y-1">
                                    {fb.evidence.map((item, i) => (
                                      <li key={i} className="text-sm" style={{ color: COLORS.black }}>
                                        {item}
                                      </li>
                                    ))}
                                  </ul>
                                </FeedbackSection>

                                {/* Execution path */}
                                <FeedbackSection title="Execution Path">
                                  <ol className="list-decimal list-inside space-y-1">
                                    {fb.execution_path.map((step, i) => (
                                      <li key={i} className="text-sm" style={{ color: COLORS.black }}>
                                        {step}
                                      </li>
                                    ))}
                                  </ol>
                                </FeedbackSection>

                                {/* Diagram */}
                                {result.diagram_svg && (
                                  <FeedbackSection title="Execution Diagram">
                                    <div
                                      className="overflow-x-auto rounded-lg border p-2"
                                      style={{ borderColor: COLORS.goldLight }}
                                      dangerouslySetInnerHTML={{ __html: result.diagram_svg }}
                                    />
                                  </FeedbackSection>
                                )}

                                {/* Why it matters */}
                                <FeedbackSection title="Why It Matters">
                                  <p className="text-sm" style={{ color: COLORS.black }}>{fb.why_it_matters}</p>
                                </FeedbackSection>

                                {/* Suggested changes */}
                                <FeedbackSection title="Suggested Changes">
                                  <ul className="list-disc list-inside space-y-1">
                                    {fb.suggested_changes.map((change, i) => (
                                      <li key={i} className="text-sm" style={{ color: COLORS.black }}>
                                        {change}
                                      </li>
                                    ))}
                                  </ul>
                                </FeedbackSection>

                                {/* Example fix, if provided */}
                                {fb.example_fix && (
                                  <FeedbackSection title="Example">
                                    <pre
                                      className="text-xs p-3 rounded-lg overflow-x-auto"
                                      style={{ backgroundColor: COLORS.black, color: COLORS.white }}
                                    >
                                      <code>{fb.example_fix}</code>
                                    </pre>
                                  </FeedbackSection>
                                )}

                                {/* Check your understanding */}
                                <div
                                  className="p-4 rounded-xl border"
                                  style={{ borderColor: COLORS.gold, backgroundColor: COLORS.goldLight + "60" }}
                                >
                                  <p className="text-xs font-semibold uppercase tracking-wide mb-1" style={{ color: COLORS.black }}>
                                    Check Your Understanding
                                  </p>
                                  <p className="text-sm" style={{ color: COLORS.black }}>{fb.check_your_understanding}</p>
                                </div>

                                {/* Confidence badge */}
                                <div className="flex items-center gap-2">
                                  <span className="text-xs font-medium" style={{ color: COLORS.black }}>
                                    Confidence:
                                  </span>
                                  <span
                                    className="text-xs font-semibold px-2 py-0.5 rounded-full"
                                    style={{
                                      backgroundColor:
                                        fb.confidence === "high"
                                          ? COLORS.blueLight
                                          : fb.confidence === "medium"
                                            ? COLORS.goldLight
                                            : COLORS.redDark + "20",
                                      color:
                                        fb.confidence === "high"
                                          ? COLORS.blueDark
                                          : fb.confidence === "medium"
                                            ? COLORS.black
                                            : COLORS.red,
                                    }}
                                  >
                                    {fb.confidence}
                                  </span>
                                </div>
                              </>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </div>
      </main>

      <footer className="mt-auto border-t-4" style={{ backgroundColor: COLORS.black, borderColor: COLORS.gold }}>
        <div className="py-7">
          <ul className="flex flex-row justify-center gap-6 list-none">
            <li>
              <Link href="/research" className="text-white hover:opacity-80" style={{ color: COLORS.white }}>
                Research Information
              </Link>
            </li>

            <li>
              <Link href="/about-us" className="text-white hover:opacity-80" style={{ color: COLORS.white }}>
                Team & Organisation
              </Link>
            </li>
          </ul>

        </div>
      </footer>

    </div>
  );
}