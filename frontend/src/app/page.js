"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import UploadBox from "./components/upload";
import Feedback from "./components/feedback";
import CodePreview from "./components/codePreview";
import UploadInfo from "./components/uploadInfo"
import { COLORS } from "./components/colors"
import Link from "next/link"
import { Group, Panel, Separator } from "react-resizable-panels";

const PANEL = { NONE: "none", STAGING: "staging", RESULTS: "results" };

export default function Home() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [panelMode, setPanelMode] = useState(PANEL.NONE);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [Assignments, setAssignments] = useState([]);
  const [compilationMode, setCompilationMode] = useState("independent");
  const [previewFile, setPreviewFile] = useState(null); // null = closed
  const fileInputRef = useRef(null);
  const folderInputRef = useRef(null);
  const [submissionId, setSubmissionId] = useState(null);

  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => setError(null), 7000);
    return () => clearTimeout(timer);
  }, [error]);

  const ALLOWED_EXTENSIONS = [".cpp", ".h"];
  const hasAllowedExtension = (filename) =>
    ALLOWED_EXTENSIONS.some((ext) => filename.toLowerCase().endsWith(ext));

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files).filter((f) => hasAllowedExtension(f.name));
    setSelectedFiles((prev) => {
      const existingKeys = new Set(prev.map((f) => f.webkitRelativePath || f.name));
      const newOnes = files.filter((f) => !existingKeys.has(f.webkitRelativePath || f.name));
      return [...prev, ...newOnes];
    });
    setPanelMode(PANEL.STAGING);
    e.target.value = "";
  };

  const removeFile = (indexToRemove) => {
    setSelectedFiles((prev) => {
      const next = prev.filter((_, i) => i !== indexToRemove);
      if (next.length === 0) setPanelMode(PANEL.NONE);
      return next;
    });
  };

  const clearAllFiles = () => {
    setSelectedFiles([]);
    setPanelMode(PANEL.NONE);
  };

  const STAGE_LABELS = {
    discovering_files: "Scanning submission files…",
    running_model_checker: "Running ESBMC model checker",
    parsing_output: "Parsing verification output",
    generating_feedback: "Generating pedagogical feedback",
    rendering_diagram: "Rendering execution diagram",
    done: "Finalizing…",
  };

  const [stageLabel, setStageLabel] = useState(null);

  const MIN_STAGE_DISPLAY_MS = 500;
  const stageStateRef = useRef({ lastUpdate: 0, pending: null });

  const applyStageWithMinDelay = useCallback((label) => {
    const state = stageStateRef.current;
    const now = Date.now();
    const elapsed = now - state.lastUpdate;

    if (state.pending) clearTimeout(state.pending);

    if (elapsed >= MIN_STAGE_DISPLAY_MS) {
      setStageLabel(label);
      state.lastUpdate = now;
    } else {
      state.pending = setTimeout(() => {
        setStageLabel(label);
        state.lastUpdate = Date.now();
      }, MIN_STAGE_DISPLAY_MS - elapsed);
    }
  }, []);

  const generateFeedback = async (submissionIdToUse) => {
    setLoading(true);
    setAssignments([]);
    applyStageWithMinDelay(STAGE_LABELS.discovering_files);

    try {
      const res = await fetch("http://localhost:8000/api/feedback/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          submission_id: submissionIdToUse,
          compilation_mode: compilationMode,
        }),
      });

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split("\n\n");
        buffer = parts.pop();

        for (const part of parts) {
          if (!part.startsWith("data: ")) continue;
          const event = JSON.parse(part.slice(6));

          if (event.type === "stage") {
            const label = STAGE_LABELS[event.stage] || event.stage;
            applyStageWithMinDelay(event.detail ? `${label} (${event.detail})` : label);
          } else if (event.type === "result") {
            setAssignments([event.data]);
          } else if (event.type === "error") {
            throw new Error(event.detail);
          }
        }
      }
    } catch (err) {
      setError(err.message || "Feedback generation failed. Please try again.");
    } finally {
      if (stageStateRef.current.pending) clearTimeout(stageStateRef.current.pending);
      setLoading(false);
      setStageLabel(null);
    }
  };

  const deleteCall = async () => {
    if (submissionId) {
      try {
        await fetch(`http://localhost:8000/api/submissions/${submissionId}`, {
          method: "DELETE",
        });
      } catch (err) {
        console.error("Failed to delete submission:", err);
      }
    }
  }

  const closePanel = async () => {
    if (panelMode === PANEL.STAGING) setSelectedFiles([]);

    await deleteCall();

    setUploadedFiles([]);
    setAssignments([]);
    setPanelMode(PANEL.NONE);
    setPreviewFile(null);
    setSubmissionId(null);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0) {
      setError("Select at least one file before uploading.");
      return;
    }

    setUploadedFiles(selectedFiles);
    setSelectedFiles([]);
    setPanelMode(PANEL.RESULTS);
    setPreviewFile(null);

    const formData = new FormData();
    selectedFiles.forEach((file) => {
      formData.append("files", file);
      formData.append("relative_paths", file.webkitRelativePath || file.name);
    });

    try {
      const uploadRes = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });
      if (!uploadRes.ok) {
        const errBody = await uploadRes.json().catch(() => ({}));
        throw new Error(errBody.detail || `Upload failed with status ${uploadRes.status}`);
      }
      const uploadData = await uploadRes.json();
      setSubmissionId(uploadData.submission_id);

      await generateFeedback(uploadData.submission_id);
    } catch (err) {
      setError(err.message || "Upload failed. Please try again.");
      setPanelMode(PANEL.NONE);
    }
  };

  const showRightPanel = panelMode !== PANEL.NONE;
  const previewOpen = previewFile !== null;

  const gridColsClass = !showRightPanel
    ? "grid-cols-1 place-items-center"
    : previewOpen
      ? "grid-cols-1 lg:grid-cols-2"
      : "grid-cols-1 lg:grid-cols-3";

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
        <div className={`grid gap-8 w-full transition-all duration-500 ${gridColsClass}`}>
          {!previewOpen && (
            <UploadBox
              showRightPanel={showRightPanel}
              error={error}
              setError={setError}
              uploadedFiles={uploadedFiles}
              fileInputRef={fileInputRef}
              folderInputRef={folderInputRef}
              handleFileUpload={handleFileUpload}
            />
          )}

          {panelMode === PANEL.STAGING && !previewOpen && (
            <UploadInfo
              selectedFiles={selectedFiles}
              removeFile={removeFile}
              clearAllFiles={clearAllFiles}
              compilationMode={compilationMode}
              setCompilationMode={setCompilationMode}
              handleUpload={handleUpload}
            />
          )}

          {panelMode === PANEL.RESULTS && !previewOpen && (
            <Feedback
              loading={loading}
              stageLabel={stageLabel}
              assignments={Assignments}
              onClosePanel={closePanel}
              onPreview={(file) => setPreviewFile(file)}
              previewOpen={previewOpen}
            />
          )}

          {panelMode === PANEL.RESULTS && previewOpen && (
            <div className="lg:col-span-2">
              <Group orientation="horizontal">
                <Panel defaultSize="50%" minSize="30%" maxSize="70%">
                  <Feedback
                    loading={loading}
                    assignments={Assignments}
                    onClosePanel={closePanel}
                    onPreview={(file) => setPreviewFile(file)}
                    previewOpen={previewOpen}
                  />
                </Panel>

                <Separator
                  className="flex items-center justify-center"
                  style={{ width: "10px", cursor: "col-resize" }}
                >
                  <div
                    style={{
                      width: "3px",
                      height: "48px",
                      borderRadius: "9999px",
                      backgroundColor: COLORS.gold,
                    }}
                  />
                </Separator>

                <Panel defaultSize="50%" minSize="30%" maxSize="70%">
                  <CodePreview
                    submissionId={submissionId}
                    initialFile={previewFile}
                    onClose={() => setPreviewFile(null)}
                    onSaved={() => generateFeedback(submissionId)}
                  />
                </Panel>
              </Group>
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