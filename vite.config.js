import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const rootDir = dirname(fileURLToPath(import.meta.url));

function readJsonBody(req) {
  return new Promise((resolveBody, rejectBody) => {
    let raw = "";

    req.on("data", (chunk) => {
      raw += chunk;
    });
    req.on("end", () => {
      try {
        resolveBody(JSON.parse(raw || "{}"));
      } catch (error) {
        rejectBody(error);
      }
    });
    req.on("error", rejectBody);
  });
}

function runAnalysis(input) {
  return new Promise((resolveResult, rejectResult) => {
    const child = spawn("python", [resolve(rootDir, "ui_adapter", "analyze.py")], {
      cwd: rootDir,
      stdio: ["pipe", "pipe", "pipe"],
    });

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    child.on("error", rejectResult);
    child.on("close", (code) => {
      if (code !== 0) {
        rejectResult(new Error(stderr || `Analysis process exited with code ${code}.`));
        return;
      }

      try {
        resolveResult(JSON.parse(stdout));
      } catch (error) {
        rejectResult(error);
      }
    });

    child.stdin.write(JSON.stringify({ input }));
    child.stdin.end();
  });
}

function xrayApiPlugin() {
  const handler = async (req, res, next) => {
    if (req.method !== "POST" || req.url !== "/api/analyze") {
      next();
      return;
    }

    try {
      const body = await readJsonBody(req);
      const data = await runAnalysis(body.input ?? "");

      res.statusCode = 200;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify(data));
    } catch (error) {
      res.statusCode = 500;
      res.setHeader("Content-Type", "application/json");
      res.end(JSON.stringify({ error: error.message || "Analysis failed." }));
    }
  };

  return {
    name: "xray-api",
    configureServer(server) {
      server.middlewares.use(handler);
    },
    configurePreviewServer(server) {
      server.middlewares.use(handler);
    },
  };
}

export default defineConfig({
  plugins: [react(), xrayApiPlugin()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          recharts: ["recharts"],
        },
      },
    },
  },
});
