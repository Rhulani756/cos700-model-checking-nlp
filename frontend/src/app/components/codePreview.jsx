"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { X, FileCode2, Save, RefreshCw } from "lucide-react";
import { cpp } from "@codemirror/lang-cpp";
import { COLORS } from "./colors";

const CodeMirror = dynamic(() => import("@uiw/react-codemirror"), { ssr: false });

export default function CodePreview({ submissionId, initialFile, onClose, onSaved }) {
  const [fileList, setFileList] = useState([]);
  const [activeFile, setActiveFile] = useState(initialFile);
  const [contents, setContents] = useState({});
  const [drafts, setDrafts] = useState({});
  const [listError, setListError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`http://localhost:8000/api/files/${submissionId}`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to list files (status ${res.status})`);
        return res.json();
      })
      .then((data) => {
        if (!cancelled) setFileList(data.files.map((f) => f.path));
      })
      .catch((err) => {
        if (!cancelled) setListError(err.message);
      });
    return () => { cancelled = true; };
  }, [submissionId]);

  useEffect(() => {
    if (!activeFile || contents[activeFile] !== undefined) return;
    let cancelled = false;
    fetch(
      `http://localhost:8000/api/files/${submissionId}/content?path=${encodeURIComponent(activeFile)}`
    )
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to load file (status ${res.status})`);
        return res.json();
      })
      .then((data) => {
        if (!cancelled) {
          setContents((prev) => ({ ...prev, [activeFile]: data.content }));
          setDrafts((prev) => ({ ...prev, [activeFile]: data.content }));
        }
      })
      .catch(() => {
        if (!cancelled) {
          setContents((prev) => ({ ...prev, [activeFile]: "// Failed to load file." }));
          setDrafts((prev) => ({ ...prev, [activeFile]: "// Failed to load file." }));
        }
      });
    return () => { cancelled = true; };
  }, [activeFile, submissionId, contents]);

  const isLoadingActiveFile = activeFile !== null && contents[activeFile] === undefined;
  const draft = drafts[activeFile] ?? "";
  const hasChanges = activeFile !== null && draft !== contents[activeFile];

  const handleSave = async (reverify) => {
    setSaving(true);
    setSaveError(null);
    try {
      const res = await fetch(
        `http://localhost:8000/api/files/${submissionId}/content?path=${encodeURIComponent(activeFile)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content: draft }),
        }
      );
      if (!res.ok) {
        const errBody = await res.json().catch(() => ({}));
        throw new Error(errBody.detail || `Save failed with status ${res.status}`);
      }
      setContents((prev) => ({ ...prev, [activeFile]: draft }));
      if (reverify && onSaved) {
        onSaved();
      }
    } catch (err) {
      setSaveError(err.message || "Save failed.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="lg:col-span-2">
      <div className="rounded-xl border overflow-hidden" style={{ borderColor: COLORS.gold, backgroundColor: COLORS.white }}>
        <div
          className="flex items-center justify-between px-4 py-3 border-b"
          style={{ borderColor: COLORS.goldLight, backgroundColor: COLORS.goldLight + "60" }}
        >
          <div className="flex items-center gap-2">
            <p className="text-sm font-semibold" style={{ color: COLORS.black }}>Code Preview</p>
          </div>
          <div className="flex items-center gap-2">
            {hasChanges && (
                <button
                  type="button"
                  onClick={() => handleSave(true)}
                  disabled={saving}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-white"
                  style={{ backgroundColor: COLORS.blue }}
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  {saving ? "Saving…" : "Re-check"}
                </button>

            )}
            <button
              type="button"
              onClick={onClose}
              aria-label="Close preview"
              className="p-1 rounded-md hover:opacity-80"
              style={{ color: COLORS.black }}
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {listError && <p className="text-sm p-4" style={{ color: COLORS.red }}>{listError}</p>}
        {saveError && <p className="text-sm px-4 pt-2" style={{ color: COLORS.red }}>{saveError}</p>}

        {fileList.length > 1 && (
          <div className="flex gap-1 px-2 pt-2 overflow-x-auto border-b" style={{ borderColor: COLORS.goldLight }}>
            {fileList.map((path) => (
              <button
                key={path}
                type="button"
                onClick={() => setActiveFile(path)}
                className="flex items-center gap-1 px-3 py-2 text-xs font-medium rounded-t-md whitespace-nowrap"
                style={{
                  backgroundColor: activeFile === path ? COLORS.goldLight : "transparent",
                  color: activeFile === path ? COLORS.black : COLORS.black + "88",
                }}
              >
                <FileCode2 className="w-3.5 h-3.5" />
                {path}
                {drafts[path] !== undefined && drafts[path] !== contents[path] && " •"}
              </button>
            ))}
          </div>
        )}

        <div className="max-h-[32rem] overflow-auto">
          {isLoadingActiveFile ? (
            <p className="text-sm p-4" style={{ color: COLORS.black }}>Loading…</p>
          ) : (
            <CodeMirror
              value={draft}
              height="32rem"
              theme="light"
              extensions={[cpp()]}
              onChange={(value) => setDrafts((prev) => ({ ...prev, [activeFile]: value }))}
              basicSetup={{
                lineNumbers: true,
                foldGutter: true,
                highlightActiveLine: true,
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}