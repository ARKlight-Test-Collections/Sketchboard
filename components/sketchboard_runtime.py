# include <stdlib.ARKlight>

from arklight.backend.script_extension import ScriptExtension

class SketchboardRuntime(ScriptExtension):
        script = r"""<script>
(function () {
    "use strict";

    function startSketchboard() {
        var host = document.getElementById("drawing-host");
        if (!host || host.dataset.sketchboardReady) return;
        host.dataset.sketchboardReady = "true";

        var canvas = document.createElement("canvas");
        canvas.id = "drawing-canvas";
        canvas.className = "drawing-surface";
        canvas.setAttribute("aria-label", "Interactive sketchboard canvas");
        canvas.setAttribute("role", "img");
        canvas.tabIndex = 0;
        host.appendChild(canvas);

        var context = canvas.getContext("2d");
        var storageKey = "arklight:sketchboard:v1";
        var colors = {
            ink: "#27364b", blue: "#4169e1", rose: "#df697d",
            green: "#3a9278", amber: "#d99a32", violet: "#8b6dc1"
        };
        var state = {
            elements: [], selectedId: null, selectedIds: [], tool: "selection", stroke: colors.ink,
            fill: "#dbeafe", fillEnabled: false, strokeWidth: 2, strokeStyle: "solid",
            opacity: 1, fontSize: 20, gridVisible: true, snapToGrid: false,
            background: "#ffffff", sceneName: byId("board-title").value || "Untitled board",
            zoom: 1, panX: 0, panY: 0, preview: null,
            marquee: null, clipboard: []
        };
        var history = [];
        var historyIndex = 0;
        var gesture = null;
        var spaceDown = false;
        var sequence = 0;
        var imageCache = Object.create(null);

        function clone(value) {
            return JSON.parse(JSON.stringify(value));
        }

        function byId(id) {
            return document.getElementById(id);
        }

        function setText(id, value) {
            var node = byId(id);
            if (node) node.textContent = value;
        }

        function setSelection(ids) {
            var unique = Array.from(new Set(ids));
            var groups = state.elements.filter(function (element) { return unique.indexOf(element.id) !== -1 && element.groupId; }).map(function (element) { return element.groupId; });
            state.elements.forEach(function (element) {
                if (element.groupId && groups.indexOf(element.groupId) !== -1 && unique.indexOf(element.id) === -1) unique.push(element.id);
            });
            state.selectedIds = unique;
            state.selectedId = state.selectedIds[0] || null;
        }

        function selectedElements() {
            return state.elements.filter(function (element) { return state.selectedIds.indexOf(element.id) !== -1; });
        }

        function sceneSnapshot() {
            return {
                elements: clone(state.elements), background: state.background,
                stroke: state.stroke, fill: state.fill, fillEnabled: state.fillEnabled,
                strokeWidth: state.strokeWidth, strokeStyle: state.strokeStyle,
                opacity: state.opacity, fontSize: state.fontSize,
                gridVisible: state.gridVisible, snapToGrid: state.snapToGrid,
                sceneName: state.sceneName
            };
        }

        function applyControls() {
            byId("background-color").value = state.background;
            byId("stroke-color").value = state.stroke;
            byId("fill-color").value = state.fill;
            byId("stroke-width").value = state.strokeWidth;
            byId("line-style").value = state.strokeStyle;
            byId("element-opacity").value = Math.round(state.opacity * 100);
            byId("font-size").value = state.fontSize;
            var titleInput = byId("board-title");
            if (titleInput.value !== state.sceneName) {
                titleInput.value = state.sceneName;
                titleInput.dispatchEvent(new Event("input", { bubbles: true }));
            }
            byId("snap-toggle").setAttribute("aria-pressed", state.snapToGrid ? "true" : "false");
            byId("snap-toggle").textContent = state.snapToGrid ? "Snap on" : "Snap off";
            byId("grid-toggle").setAttribute("aria-pressed", state.gridVisible ? "true" : "false");
            byId("grid-toggle").textContent = state.gridVisible ? "Hide grid" : "Show grid";
            setText("stroke-width-value", state.strokeWidth + " px");
            setText("opacity-value", Math.round(state.opacity * 100) + "%");
            setText("font-size-value", state.fontSize + " px");
        }

        function restoreSnapshot(snapshot) {
            state.elements = clone(snapshot.elements);
            state.background = snapshot.background;
            state.stroke = snapshot.stroke;
            state.fill = snapshot.fill;
            state.fillEnabled = snapshot.fillEnabled;
            state.strokeWidth = snapshot.strokeWidth;
            state.strokeStyle = snapshot.strokeStyle || "solid";
            state.opacity = snapshot.opacity == null ? 1 : snapshot.opacity;
            state.fontSize = snapshot.fontSize || 20;
            state.gridVisible = snapshot.gridVisible !== false;
            state.snapToGrid = snapshot.snapToGrid === true;
            state.sceneName = snapshot.sceneName || "Untitled board";
            setSelection([]);
        }

        function download(blob, filename) {
            var link = document.createElement("a");
            var url = URL.createObjectURL(blob);
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            link.remove();
            window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        }

        function sceneData() {
            return {
                type: "sketchboard",
                version: 2,
                elements: state.elements,
                appState: {
                    name: state.sceneName,
                    viewBackgroundColor: state.background,
                    gridVisible: state.gridVisible,
                    snapToGrid: state.snapToGrid,
                    stroke: state.stroke,
                    fill: state.fill,
                    fillEnabled: state.fillEnabled,
                    strokeWidth: state.strokeWidth,
                    strokeStyle: state.strokeStyle,
                    opacity: state.opacity,
                    fontSize: state.fontSize
                }
            };
        }

        function normalizeElement(element, files) {
            if (!element || typeof element.id !== "string") return null;
            var type = String(element.type || "").toLowerCase();
            if (["rectangle", "diamond", "ellipse", "line", "arrow", "freedraw", "text", "image"].indexOf(type) === -1) return null;
            var isExcalidraw = Object.prototype.hasOwnProperty.call(element, "width") || Object.prototype.hasOwnProperty.call(element, "strokeColor");
            var x = Number(element.x) || 0;
            var y = Number(element.y) || 0;
            var width = Number(isExcalidraw ? element.width : element.w) || 0;
            var height = Number(isExcalidraw ? element.height : element.h) || 0;
            var points = Array.isArray(element.points) ? element.points.slice(0, 20000).map(function (point) {
                if (Array.isArray(point)) return { x: x + (Number(point[0]) || 0), y: y + (Number(point[1]) || 0) };
                return { x: Number(point.x) || 0, y: Number(point.y) || 0 };
            }) : [];
            var imageSrc = element.imageSrc || "";
            if (type === "image" && isExcalidraw && files && files[element.fileId]) imageSrc = files[element.fileId].dataURL || "";
            if (type === "image" && !/^data:image\//i.test(imageSrc)) return null;
            return {
                id: element.id,
                type: type,
                x: x,
                y: y,
                w: width,
                h: height,
                points: points,
                text: String(element.text || ""),
                imageSrc: imageSrc,
                angle: Number(element.angle) || 0,
                groupId: Array.isArray(element.groupIds) && element.groupIds.length ? element.groupIds[0] : element.groupId || null,
                stroke: /^#[0-9a-f]{6}$/i.test(element.strokeColor || element.stroke || "") ? (element.strokeColor || element.stroke) : state.stroke,
                fill: element.backgroundColor === "transparent" ? "transparent" : (/^#[0-9a-f]{6}$/i.test(element.backgroundColor || element.fill || "") ? (element.backgroundColor || element.fill) : "transparent"),
                strokeWidth: Math.max(1, Math.min(12, Number(element.strokeWidth) || 2)),
                strokeStyle: ["solid", "dashed", "dotted"].indexOf(element.strokeStyle) !== -1 ? element.strokeStyle : "solid",
                opacity: Math.max(0.1, Math.min(1, Number(element.opacity == null ? 100 : element.opacity) / (isExcalidraw || Number(element.opacity) > 1 ? 100 : 1))),
                fontSize: Math.max(8, Math.min(96, Number(element.fontSize) || state.fontSize))
            };
        }

        function normalizeScene(incoming) {
            if (!incoming || !Array.isArray(incoming.elements)) throw new Error("Scene elements are missing");
            var files = incoming.files || {};
            var elements = incoming.elements.filter(function (element) { return !element.isDeleted; }).slice(0, 5000).map(function (element) {
                return normalizeElement(element, files);
            }).filter(Boolean);
            var appState = incoming.appState || {};
            var background = incoming.background || appState.viewBackgroundColor || "#ffffff";
            if (!/^#[0-9a-f]{6}$/i.test(background)) background = "#ffffff";
            var oldStyle = incoming.type === "sketchboard" || incoming.version === 1;
            return {
                elements: elements,
                background: background,
                gridVisible: oldStyle && appState.gridVisible === false ? false : true,
                snapToGrid: oldStyle && appState.snapToGrid === true,
                sceneName: String(appState.name || incoming.name || "Untitled board").slice(0, 100),
                stroke: /^#[0-9a-f]{6}$/i.test(appState.stroke || incoming.stroke || "") ? (appState.stroke || incoming.stroke) : state.stroke,
                fill: /^#[0-9a-f]{6}$/i.test(appState.fill || incoming.fill || "") ? (appState.fill || incoming.fill) : state.fill,
                fillEnabled: appState.fillEnabled === true || incoming.fillEnabled === true,
                strokeWidth: Math.max(1, Math.min(12, Number(appState.strokeWidth || incoming.strokeWidth) || state.strokeWidth)),
                strokeStyle: appState.strokeStyle || "solid",
                opacity: Number(appState.opacity) || 1,
                fontSize: Number(appState.fontSize) || 20
            };
        }

        function toExcalidrawElement(element) {
            var common = {
                id: element.id,
                type: element.type,
                x: element.x,
                y: element.y,
                width: element.w,
                height: element.h,
                angle: element.angle || 0,
                strokeColor: element.stroke,
                backgroundColor: element.fill || "transparent",
                fillStyle: "solid",
                strokeWidth: element.strokeWidth || 2,
                strokeStyle: element.strokeStyle || "solid",
                roughness: 1,
                opacity: Math.round((element.opacity == null ? 1 : element.opacity) * 100),
                groupIds: element.groupId ? [element.groupId] : [],
                frameId: null,
                roundness: element.type === "rectangle" ? { type: 3 } : null,
                seed: Math.floor(Math.random() * 2147483647),
                version: 1,
                versionNonce: Math.floor(Math.random() * 2147483647),
                isDeleted: false,
                boundElements: null,
                updated: Date.now(),
                link: null,
                locked: false
            };
            if (element.type === "freedraw") {
                common.points = element.points.map(function (point) { return [point.x - element.x, point.y - element.y]; });
                common.pressures = [];
                common.simulatePressure = false;
                common.lastCommittedPoint = null;
            }
            if (element.type === "line" || element.type === "arrow") {
                common.points = [[0, 0], [element.w, element.h]];
                common.lastCommittedPoint = null;
                common.startArrowhead = null;
                common.endArrowhead = element.type === "arrow" ? "arrow" : null;
            }
            if (element.type === "text") {
                common.fontSize = element.fontSize || 20;
                common.fontFamily = 1;
                common.text = element.text;
                common.originalText = element.text;
                common.textAlign = "left";
                common.verticalAlign = "top";
                common.baseline = common.fontSize;
                common.lineHeight = 1.25;
                common.containerId = null;
                common.autoResize = true;
            }
            if (element.type === "image") {
                common.fileId = element.id;
                common.status = "saved";
                common.scale = [1, 1];
                common.crop = null;
            }
            return common;
        }

        function exportSceneData() {
            var files = {};
            var elements = state.elements.map(function (element) {
                if (element.type === "image") files[element.id] = { id: element.id, mimeType: element.imageSrc.split(";")[0].replace("data:", ""), dataURL: element.imageSrc, created: Date.now(), lastRetrieved: Date.now() };
                return toExcalidrawElement(element);
            });
            return {
                type: "excalidraw",
                version: 2,
                source: "https://excalidraw.com",
                elements: elements,
                appState: { name: state.sceneName, viewBackgroundColor: state.background, gridSize: state.snapToGrid ? 22 : null },
                files: files
            };
        }

        function persist() {
            try {
                localStorage.setItem(storageKey, JSON.stringify(sceneData()));
                setText("save-status", "Saved in this browser");
            } catch (error) {
                setText("save-status", "Local save unavailable");
            }
        }

        function loadSaved() {
            try {
                var saved = JSON.parse(localStorage.getItem(storageKey) || "null");
                if (!saved || !Array.isArray(saved.elements)) return;
                var imported = normalizeScene(saved);
                state.elements = imported.elements;
                state.background = imported.background;
                state.sceneName = imported.sceneName;
                state.gridVisible = imported.gridVisible;
                state.snapToGrid = imported.snapToGrid;
                state.stroke = imported.stroke;
                state.fill = imported.fill;
                state.fillEnabled = imported.fillEnabled;
                state.strokeWidth = imported.strokeWidth;
                state.strokeStyle = imported.strokeStyle;
                state.opacity = imported.opacity;
                state.fontSize = imported.fontSize;
                setSelection([]);
                history = [sceneSnapshot()];
                historyIndex = 0;
                applyControls();
            } catch (error) {
                setText("save-status", "Saved scene could not be read");
            }
        }

        function resizeCanvas() {
            var rect = host.getBoundingClientRect();
            var ratio = Math.max(1, window.devicePixelRatio || 1);
            canvas.width = Math.max(1, Math.round(rect.width * ratio));
            canvas.height = Math.max(1, Math.round(rect.height * ratio));
            render();
        }

        function viewportPoint(event) {
            var rect = canvas.getBoundingClientRect();
            return { x: event.clientX - rect.left, y: event.clientY - rect.top };
        }

        function scenePoint(event) {
            var point = viewportPoint(event);
            var scene = { x: (point.x - state.panX) / state.zoom, y: (point.y - state.panY) / state.zoom };
            if (state.snapToGrid) {
                scene.x = Math.round(scene.x / 22) * 22;
                scene.y = Math.round(scene.y / 22) * 22;
            }
            return scene;
        }

        function boundsOf(element) {
            if (element.type === "freedraw") {
                var xs = element.points.map(function (point) { return point.x; });
                var ys = element.points.map(function (point) { return point.y; });
                return { x: Math.min.apply(null, xs), y: Math.min.apply(null, ys), w: Math.max.apply(null, xs) - Math.min.apply(null, xs), h: Math.max.apply(null, ys) - Math.min.apply(null, ys) };
            }
            if (element.type === "line" || element.type === "arrow") {
                return { x: Math.min(element.x, element.x + element.w), y: Math.min(element.y, element.y + element.h), w: Math.abs(element.w), h: Math.abs(element.h) };
            }
            if (element.type === "text") {
                var fontSize = element.fontSize || state.fontSize;
                var lines = String(element.text || "").split("\n");
                var maxLine = lines.reduce(function (longest, line) { return Math.max(longest, line.length); }, 0);
                return { x: element.x, y: element.y - fontSize, w: Math.max(30, maxLine * fontSize * 0.62), h: Math.max(fontSize * 1.25, lines.length * fontSize * 1.25) };
            }
            return { x: Math.min(element.x, element.x + element.w), y: Math.min(element.y, element.y + element.h), w: Math.abs(element.w), h: Math.abs(element.h) };
        }

        function hitTest(point) {
            for (var index = state.elements.length - 1; index >= 0; index -= 1) {
                var element = state.elements[index];
                var box = boundsOf(element);
                var pad = Math.max(8, element.strokeWidth || 2);
                if (point.x >= box.x - pad && point.x <= box.x + box.w + pad && point.y >= box.y - pad && point.y <= box.y + box.h + pad) return element;
            }
            return null;
        }

        function handleAt(point, box) {
            if (!box) return null;
            var tolerance = 9 / state.zoom;
            return resizeHandles(box).find(function (handle) {
                return Math.abs(point.x - handle.x) <= tolerance && Math.abs(point.y - handle.y) <= tolerance;
            }) || null;
        }

        function boxesIntersect(a, b) {
            return a.x <= b.x + b.w && a.x + a.w >= b.x && a.y <= b.y + b.h && a.y + a.h >= b.y;
        }

        function draggedBounds(start, end) {
            return { x: Math.min(start.x, end.x), y: Math.min(start.y, end.y), w: Math.abs(end.x - start.x), h: Math.abs(end.y - start.y) };
        }

        function resizeBounds(box, handle, dx, dy) {
            var left = box.x;
            var right = box.x + box.w;
            var top = box.y;
            var bottom = box.y + box.h;
            if (handle.id.indexOf("w") !== -1) left += dx;
            if (handle.id.indexOf("e") !== -1) right += dx;
            if (handle.id.indexOf("n") !== -1) top += dy;
            if (handle.id.indexOf("s") !== -1) bottom += dy;
            if (right - left < 4) right = left + 4;
            if (bottom - top < 4) bottom = top + 4;
            return { x: left, y: top, w: right - left, h: bottom - top };
        }

        function resizeElementTo(element, originalBounds, nextBounds) {
            var resized = clone(element);
            var scaleX = originalBounds.w ? nextBounds.w / originalBounds.w : 1;
            var scaleY = originalBounds.h ? nextBounds.h / originalBounds.h : 1;
            if (element.type === "freedraw") {
                resized.points = element.points.map(function (point) {
                    return {
                        x: nextBounds.x + (point.x - originalBounds.x) * scaleX,
                        y: nextBounds.y + (point.y - originalBounds.y) * scaleY
                    };
                });
                return resized;
            }
            if (element.type === "text") {
                resized.x = nextBounds.x;
                resized.y = element.y + (nextBounds.h - originalBounds.h);
                resized.fontSize = Math.max(8, Math.min(96, Math.round((element.fontSize || state.fontSize) * scaleY)));
                return resized;
            }
            if (element.type === "line" || element.type === "arrow") {
                var directionX = Math.sign(element.w) || 1;
                var directionY = Math.sign(element.h) || 1;
                resized.x = directionX > 0 ? nextBounds.x : nextBounds.x + nextBounds.w;
                resized.y = directionY > 0 ? nextBounds.y : nextBounds.y + nextBounds.h;
                resized.w = directionX * nextBounds.w;
                resized.h = directionY * nextBounds.h;
                return resized;
            }
            resized.x = nextBounds.x;
            resized.y = nextBounds.y;
            resized.w = nextBounds.w;
            resized.h = nextBounds.h;
            return resized;
        }

        function pathFor(element) {
            context.beginPath();
            if (element.type === "rectangle") {
                context.rect(element.x, element.y, element.w, element.h);
            } else if (element.type === "ellipse") {
                context.ellipse(element.x + element.w / 2, element.y + element.h / 2, Math.max(0.5, Math.abs(element.w / 2)), Math.max(0.5, Math.abs(element.h / 2)), 0, 0, Math.PI * 2);
            } else if (element.type === "diamond") {
                context.moveTo(element.x + element.w / 2, element.y);
                context.lineTo(element.x + element.w, element.y + element.h / 2);
                context.lineTo(element.x + element.w / 2, element.y + element.h);
                context.lineTo(element.x, element.y + element.h / 2);
                context.closePath();
            } else if (element.type === "freedraw") {
                if (!element.points.length) return;
                context.moveTo(element.points[0].x, element.points[0].y);
                element.points.slice(1).forEach(function (point) { context.lineTo(point.x, point.y); });
            } else {
                context.moveTo(element.x, element.y);
                context.lineTo(element.x + element.w, element.y + element.h);
                if (element.type === "arrow") {
                    var angle = Math.atan2(element.h, element.w);
                    var head = Math.max(10, element.strokeWidth * 5);
                    context.moveTo(element.x + element.w, element.y + element.h);
                    context.lineTo(element.x + element.w - head * Math.cos(angle - Math.PI / 6), element.y + element.h - head * Math.sin(angle - Math.PI / 6));
                    context.moveTo(element.x + element.w, element.y + element.h);
                    context.lineTo(element.x + element.w - head * Math.cos(angle + Math.PI / 6), element.y + element.h - head * Math.sin(angle + Math.PI / 6));
                }
            }
        }

        function drawElement(element) {
            context.save();
            if (element.angle) {
                var rawBounds = boundsOf(element);
                var centerX = rawBounds.x + rawBounds.w / 2;
                var centerY = rawBounds.y + rawBounds.h / 2;
                context.translate(centerX, centerY);
                context.rotate(element.angle);
                context.translate(-centerX, -centerY);
            }
            context.strokeStyle = element.stroke;
            context.fillStyle = element.fill || "transparent";
            context.lineWidth = element.strokeWidth || 2;
            context.globalAlpha = element.opacity == null ? 1 : element.opacity;
            context.setLineDash(element.strokeStyle === "dashed" ? [8, 6] : element.strokeStyle === "dotted" ? [2, 5] : []);
            context.lineCap = "round";
            context.lineJoin = "round";
            if (element.type === "text") {
                var fontSize = element.fontSize || state.fontSize;
                context.font = fontSize + "px 'Avenir Next', 'Trebuchet MS', sans-serif";
                context.fillStyle = element.stroke;
                String(element.text || "").split("\n").forEach(function (line, index) {
                    context.fillText(line, element.x, element.y + index * fontSize * 1.25);
                });
            } else if (element.type === "image") {
                var image = imageCache[element.imageSrc];
                if (!image) {
                    image = new Image();
                    imageCache[element.imageSrc] = image;
                    image.onload = render;
                    image.src = element.imageSrc;
                }
                if (image.complete && image.naturalWidth) context.drawImage(image, element.x, element.y, element.w, element.h);
            } else {
                pathFor(element);
                if (element.fill && element.fill !== "transparent" && ["rectangle", "diamond", "ellipse"].indexOf(element.type) !== -1) {
                    context.fillStyle = element.fill;
                    context.fill();
                }
                context.stroke();
                var seed = element.id.split("").reduce(function (value, character) { return (value * 31 + character.charCodeAt(0)) >>> 0; }, 7);
                var offset = ((seed % 7) - 3) * 0.22;
                if (Math.abs(element.w || 0) + Math.abs(element.h || 0) > 14) {
                    context.translate(offset, -offset);
                    pathFor(element);
                    context.globalAlpha = 0.28;
                    context.lineWidth = Math.max(0.8, (element.strokeWidth || 2) * 0.55);
                    context.stroke();
                }
            }
            context.restore();
        }

        function selectionBounds(elements) {
            if (!elements.length) return null;
            var boxes = elements.map(boundsOf);
            var left = Math.min.apply(null, boxes.map(function (box) { return box.x; }));
            var top = Math.min.apply(null, boxes.map(function (box) { return box.y; }));
            var right = Math.max.apply(null, boxes.map(function (box) { return box.x + box.w; }));
            var bottom = Math.max.apply(null, boxes.map(function (box) { return box.y + box.h; }));
            return { x: left, y: top, w: right - left, h: bottom - top };
        }

        function resizeHandles(box) {
            return [
                { id: "nw", x: box.x, y: box.y },
                { id: "n", x: box.x + box.w / 2, y: box.y },
                { id: "ne", x: box.x + box.w, y: box.y },
                { id: "e", x: box.x + box.w, y: box.y + box.h / 2 },
                { id: "se", x: box.x + box.w, y: box.y + box.h },
                { id: "s", x: box.x + box.w / 2, y: box.y + box.h },
                { id: "sw", x: box.x, y: box.y + box.h },
                { id: "w", x: box.x, y: box.y + box.h / 2 }
            ];
        }

        function rotationHandle(box) {
            return { x: box.x + box.w / 2, y: box.y - 24 / state.zoom };
        }

        function hitRotationHandle(point, box) {
            var handle = rotationHandle(box);
            return Math.hypot(point.x - handle.x, point.y - handle.y) <= 10 / state.zoom;
        }

        function drawSelectionUI() {
            var selected = selectedElements();
            if (selected.length) {
                var box = selectionBounds(selected);
                context.save();
                context.strokeStyle = "#4169e1";
                context.lineWidth = 1 / state.zoom;
                context.setLineDash([5 / state.zoom, 4 / state.zoom]);
                context.strokeRect(box.x - 5 / state.zoom, box.y - 5 / state.zoom, box.w + 10 / state.zoom, box.h + 10 / state.zoom);
                if (selected.length > 0) {
                    context.setLineDash([]);
                    context.fillStyle = "#ffffff";
                    context.strokeStyle = "#4169e1";
                    var handleSize = 8 / state.zoom;
                    var rotateHandle = rotationHandle(box);
                    context.beginPath();
                    context.moveTo(box.x + box.w / 2, box.y);
                    context.lineTo(rotateHandle.x, rotateHandle.y);
                    context.stroke();
                    context.beginPath();
                    context.arc(rotateHandle.x, rotateHandle.y, 5 / state.zoom, 0, Math.PI * 2);
                    context.fill();
                    context.stroke();
                    resizeHandles(box).forEach(function (handle) {
                        context.fillRect(handle.x - handleSize / 2, handle.y - handleSize / 2, handleSize, handleSize);
                        context.strokeRect(handle.x - handleSize / 2, handle.y - handleSize / 2, handleSize, handleSize);
                    });
                }
                context.restore();
            }
            if (state.marquee) {
                var marquee = selectionBounds([{ x: state.marquee.x1, y: state.marquee.y1, w: state.marquee.x2 - state.marquee.x1, h: state.marquee.y2 - state.marquee.y1 }]);
                context.save();
                context.fillStyle = "rgba(65, 105, 225, 0.10)";
                context.strokeStyle = "#4169e1";
                context.setLineDash([4 / state.zoom, 3 / state.zoom]);
                context.fillRect(marquee.x, marquee.y, marquee.w, marquee.h);
                context.strokeRect(marquee.x, marquee.y, marquee.w, marquee.h);
                context.restore();
            }
        }

        function render() {
            if (!context || !canvas.width || !canvas.height) return;
            var ratio = Math.max(1, window.devicePixelRatio || 1);
            var width = canvas.width / ratio;
            var height = canvas.height / ratio;
            context.setTransform(ratio, 0, 0, ratio, 0, 0);
            context.clearRect(0, 0, width, height);
            context.fillStyle = state.background;
            context.fillRect(0, 0, width, height);
            context.save();
            context.setTransform(ratio * state.zoom, 0, 0, ratio * state.zoom, ratio * state.panX, ratio * state.panY);
            var spacing = 22;
            var startX = Math.floor((-state.panX / state.zoom) / spacing) * spacing;
            var startY = Math.floor((-state.panY / state.zoom) / spacing) * spacing;
            if (state.gridVisible) {
                context.fillStyle = "#dfe3e9";
                for (var x = startX; x < (width - state.panX) / state.zoom + spacing; x += spacing) {
                    for (var y = startY; y < (height - state.panY) / state.zoom + spacing; y += spacing) {
                        context.beginPath();
                        context.arc(x, y, 0.85, 0, Math.PI * 2);
                        context.fill();
                    }
                }
            }
            state.elements.forEach(drawElement);
            if (state.preview) drawElement(state.preview);
            drawSelectionUI();
            context.restore();
            byId("zoom-fit").textContent = Math.round(state.zoom * 100) + "%";
            updateSelectionUI();
        }

        function updateSelectionUI() {
            var selected = selectedElements();
            var primary = selected.find(function (element) { return element.id === state.selectedId; });
            setText("selection-status", selected.length > 1 ? selected.length + " elements selected" : primary ? primary.type.charAt(0).toUpperCase() + primary.type.slice(1) + " selected" : "No selection");
            setText("tool-status", state.elements.length + (state.elements.length === 1 ? " element" : " elements") + "  ·  " + state.tool.replace("freedraw", "free draw"));
            var widthInput = byId("stroke-width");
            if (primary && selected.length === 1) {
                byId("stroke-color").value = primary.stroke;
                widthInput.value = primary.strokeWidth;
                byId("fill-color").value = primary.fill && primary.fill !== "transparent" ? primary.fill : state.fill;
                byId("element-opacity").value = Math.round((primary.opacity == null ? 1 : primary.opacity) * 100);
                byId("line-style").value = primary.strokeStyle || "solid";
                byId("font-size").value = primary.fontSize || state.fontSize;
            } else {
                byId("stroke-color").value = state.stroke;
                widthInput.value = state.strokeWidth;
            }
            setText("stroke-width-value", (primary && selected.length === 1 ? primary.strokeWidth : state.strokeWidth) + " px");
            setText("opacity-value", Math.round((primary && selected.length === 1 ? primary.opacity == null ? 1 : primary.opacity : state.opacity) * 100) + "%");
            setText("font-size-value", (primary && selected.length === 1 ? primary.fontSize || state.fontSize : state.fontSize) + " px");
            byId("delete-selection").disabled = !selected.length;
            byId("duplicate-selection").disabled = !selected.length;
            byId("group-selection").disabled = selected.length < 2;
            byId("ungroup-selection").disabled = !selected.some(function (element) { return !!element.groupId; });
            byId("send-backward").disabled = !selected.length;
            byId("bring-forward").disabled = !selected.length;
        }

        function saveSnapshot() {
            var snapshot = sceneSnapshot();
            if (JSON.stringify(snapshot) === JSON.stringify(history[historyIndex])) return;
            history = history.slice(0, historyIndex + 1);
            history.push(snapshot);
            if (history.length > 101) history.shift();
            historyIndex = history.length - 1;
            persist();
            updateHistoryButtons();
        }

        function updateHistoryButtons() {
            byId("undo").disabled = historyIndex <= 0;
            byId("redo").disabled = historyIndex >= history.length - 1;
        }

        function newElement(point, tool) {
            sequence += 1;
            return {
                id: "shape-" + Date.now().toString(36) + "-" + sequence,
                type: tool,
                x: point.x,
                y: point.y,
                w: 0,
                h: 0,
                points: tool === "freedraw" ? [{ x: point.x, y: point.y }] : [],
                text: "",
                imageSrc: "",
                stroke: state.stroke,
                fill: state.fillEnabled ? state.fill : "transparent",
                strokeWidth: state.strokeWidth,
                strokeStyle: state.strokeStyle,
                opacity: state.opacity,
                fontSize: state.fontSize
            };
        }

        function moveElement(original, dx, dy) {
            var moved = clone(original);
            moved.x += dx;
            moved.y += dy;
            if (moved.points && moved.points.length) {
                moved.points = moved.points.map(function (point) { return { x: point.x + dx, y: point.y + dy }; });
            }
            return moved;
        }

        function freshElementId() {
            sequence += 1;
            return "shape-" + Date.now().toString(36) + "-" + sequence;
        }

        function duplicateSelection() {
            var groupMap = Object.create(null);
            var copies = selectedElements().map(function (element) {
                var copy = moveElement(element, 18, 18);
                copy.id = freshElementId();
                if (copy.groupId) {
                    if (!groupMap[copy.groupId]) groupMap[copy.groupId] = freshElementId();
                    copy.groupId = groupMap[copy.groupId];
                }
                return copy;
            });
            if (!copies.length) return;
            state.elements = state.elements.concat(copies);
            setSelection(copies.map(function (element) { return element.id; }));
            saveSnapshot();
            render();
        }

        function groupSelection() {
            if (state.selectedIds.length < 2) return;
            var groupId = freshElementId();
            selectedElements().forEach(function (element) { element.groupId = groupId; });
            setSelection(state.selectedIds);
            saveSnapshot();
            render();
        }

        function ungroupSelection() {
            var ids = state.selectedIds.slice();
            var changed = false;
            selectedElements().forEach(function (element) {
                if (element.groupId) { delete element.groupId; changed = true; }
            });
            if (!changed) return;
            setSelection(ids);
            saveSnapshot();
            render();
        }

        function copySelection() {
            state.clipboard = selectedElements().map(clone);
            setText("save-status", state.clipboard.length ? state.clipboard.length + " copied" : "Nothing selected");
        }

        function pasteClipboard() {
            if (!state.clipboard.length) return;
            var groupMap = Object.create(null);
            var copies = state.clipboard.map(function (element) {
                var copy = moveElement(element, 24, 24);
                copy.id = freshElementId();
                if (copy.groupId) {
                    if (!groupMap[copy.groupId]) groupMap[copy.groupId] = freshElementId();
                    copy.groupId = groupMap[copy.groupId];
                }
                return copy;
            });
            state.elements = state.elements.concat(copies);
            setSelection(copies.map(function (element) { return element.id; }));
            saveSnapshot();
            render();
        }

        function reorderSelection(direction) {
            var ids = state.selectedIds.slice();
            if (!ids.length) return;
            if (direction < 0) {
                for (var index = 1; index < state.elements.length; index += 1) {
                    if (ids.indexOf(state.elements[index].id) !== -1 && ids.indexOf(state.elements[index - 1].id) === -1) {
                        var previous = state.elements[index - 1];
                        state.elements[index - 1] = state.elements[index];
                        state.elements[index] = previous;
                    }
                }
            } else {
                for (var reverse = state.elements.length - 2; reverse >= 0; reverse -= 1) {
                    if (ids.indexOf(state.elements[reverse].id) !== -1 && ids.indexOf(state.elements[reverse + 1].id) === -1) {
                        var next = state.elements[reverse + 1];
                        state.elements[reverse + 1] = state.elements[reverse];
                        state.elements[reverse] = next;
                    }
                }
            }
            saveSnapshot();
            render();
        }

        function fitAll() {
            var box = selectionBounds(state.elements);
            if (!box || !box.w || !box.h) {
                state.zoom = 1;
                state.panX = 0;
                state.panY = 0;
            } else {
                var padding = 64;
                state.zoom = Math.max(0.2, Math.min(3, Math.min((canvas.clientWidth - padding) / box.w, (canvas.clientHeight - padding) / box.h)));
                state.panX = (canvas.clientWidth - box.w * state.zoom) / 2 - box.x * state.zoom;
                state.panY = (canvas.clientHeight - box.h * state.zoom) / 2 - box.y * state.zoom;
            }
            render();
        }

        function importImage(file) {
            var reader = new FileReader();
            reader.onload = function () {
                var image = new Image();
                image.onload = function () {
                    var scale = Math.min(1, 640 / image.naturalWidth, 480 / image.naturalHeight);
                    var width = image.naturalWidth * scale;
                    var height = image.naturalHeight * scale;
                    var raster = document.createElement("canvas");
                    raster.width = Math.max(1, Math.round(width));
                    raster.height = Math.max(1, Math.round(height));
                    raster.getContext("2d").drawImage(image, 0, 0, raster.width, raster.height);
                    var point = { x: (canvas.clientWidth / 2 - state.panX) / state.zoom - width / 2, y: (canvas.clientHeight / 2 - state.panY) / state.zoom - height / 2 };
                    var element = newElement(point, "image");
                    element.w = raster.width;
                    element.h = raster.height;
                    element.imageSrc = raster.toDataURL("image/png");
                    state.elements.push(element);
                    setSelection([element.id]);
                    saveSnapshot();
                    render();
                    setTool("selection");
                };
                image.onerror = function () { window.alert("This image could not be opened."); };
                image.src = String(reader.result);
            };
            reader.onerror = function () { window.alert("This image could not be read."); };
            reader.readAsDataURL(file);
        }

        function deleteSelection() {
            if (!state.selectedIds.length) return;
            var removed = state.selectedIds.slice();
            state.elements = state.elements.filter(function (element) { return removed.indexOf(element.id) === -1; });
            setSelection([]);
            saveSnapshot();
            render();
        }

        function pointerDown(event) {
            if (event.button !== 0 && event.pointerType !== "touch") return;
            event.preventDefault();
            canvas.setPointerCapture(event.pointerId);
            var point = scenePoint(event);
            var panMode = state.tool === "hand" || spaceDown || event.button === 1;
            if (panMode) {
                gesture = { mode: "pan", x: event.clientX, y: event.clientY, panX: state.panX, panY: state.panY };
                canvas.style.cursor = "grabbing";
                return;
            }
            if (state.tool === "selection") {
                var hit = hitTest(point);
                if (state.selectedIds.length === 1 && hit && hit.id === state.selectedId && event.detail === 2 && hit.type === "text") {
                    startTextEditor({ x: hit.x, y: hit.y }, hit);
                    return;
                }
                var selectedBox = selectionBounds(selectedElements());
                if (!event.shiftKey && state.selectedIds.length && selectedBox && hitRotationHandle(point, selectedBox)) {
                    var center = { x: selectedBox.x + selectedBox.w / 2, y: selectedBox.y + selectedBox.h / 2 };
                    gesture = {
                        mode: "rotate",
                        originals: selectedElements().map(clone),
                        center: center,
                        startAngle: Math.atan2(point.y - center.y, point.x - center.x)
                    };
                    return;
                }
                var resizeHandle = !event.shiftKey && state.selectedIds.length > 0 ? handleAt(point, selectedBox) : null;
                if (resizeHandle) {
                    gesture = { mode: "resize", handle: resizeHandle, start: point, originals: selectedElements().map(clone), originalBounds: selectedBox };
                    return;
                }
                if (hit && event.shiftKey) {
                    var nextIds = state.selectedIds.slice();
                    if (nextIds.indexOf(hit.id) === -1) nextIds.push(hit.id);
                    else nextIds = nextIds.filter(function (id) { return id !== hit.id; });
                    setSelection(nextIds);
                    updateSelectionUI();
                    render();
                    return;
                } else if (hit && state.selectedIds.indexOf(hit.id) === -1) {
                    setSelection([hit.id]);
                } else if (!hit && !event.shiftKey) {
                    setSelection([]);
                }
                if (hit && state.selectedIds.indexOf(hit.id) !== -1) {
                    gesture = { mode: "move", start: point, originals: selectedElements().map(clone) };
                } else if (!hit || event.shiftKey) {
                    state.marquee = { x1: point.x, y1: point.y, x2: point.x, y2: point.y };
                    gesture = { mode: "marquee", start: point, baseIds: event.shiftKey ? state.selectedIds.slice() : [] };
                }
                updateSelectionUI();
                render();
                return;
            }
            if (state.tool === "eraser") {
                var erase = hitTest(point);
                if (erase) {
                    state.elements = state.elements.filter(function (element) { return element.id !== erase.id; });
                    setSelection(state.selectedIds.filter(function (id) { return id !== erase.id; }));
                    saveSnapshot();
                    render();
                }
                return;
            }
            if (state.tool === "text") {
                startTextEditor(point, null);
                return;
            }
            if (state.tool === "image") { byId("image-import").click(); return; }
            gesture = { mode: "draw", element: newElement(point, state.tool) };
            state.preview = gesture.element;
            render();
        }

        function startTextEditor(point, existing) {
            var input = document.createElement("textarea");
            input.className = "text-editor-overlay";
            input.value = existing ? existing.text : "";
            input.setAttribute("aria-label", "Edit canvas text");
            input.style.position = "absolute";
            input.style.left = (state.panX + point.x * state.zoom) + "px";
            input.style.top = (state.panY + point.y * state.zoom - (existing ? (existing.fontSize || state.fontSize) : state.fontSize)) + "px";
            input.style.minWidth = Math.max(160, existing ? boundsOf(existing).w * state.zoom : 160) + "px";
            input.style.minHeight = "2.2rem";
            input.style.zIndex = "4";
            input.style.font = (existing ? existing.fontSize : state.fontSize) + "px 'Avenir Next', 'Trebuchet MS', sans-serif";
            input.style.color = existing ? existing.stroke : state.stroke;
            input.style.border = "1px solid #4169e1";
            input.style.background = "rgba(255,255,255,0.94)";
            input.style.resize = "both";
            host.appendChild(input);
            input.focus();
            if (existing) input.select();
            var finished = false;
            function finish(save) {
                if (finished) return;
                finished = true;
                if (save && input.value.trim()) {
                    if (existing) {
                        existing.text = input.value.trim();
                        existing.fontSize = state.fontSize;
                        setSelection([existing.id]);
                    } else {
                        var textElement = newElement(point, "text");
                        textElement.text = input.value.trim();
                        state.elements.push(textElement);
                        setSelection([textElement.id]);
                    }
                    saveSnapshot();
                }
                input.remove();
                render();
            }
            input.addEventListener("keydown", function (keyEvent) {
                if (keyEvent.key === "Escape") { keyEvent.preventDefault(); finish(false); }
                if (keyEvent.key === "Enter" && (keyEvent.ctrlKey || keyEvent.metaKey)) { keyEvent.preventDefault(); finish(true); }
            });
            input.addEventListener("blur", function () { finish(true); });
        }

        function pointerMove(event) {
            if (!gesture) return;
            var point = scenePoint(event);
            if (gesture.mode === "pan") {
                state.panX = gesture.panX + event.clientX - gesture.x;
                state.panY = gesture.panY + event.clientY - gesture.y;
            } else if (gesture.mode === "move") {
                gesture.originals.forEach(function (original) {
                    var index = state.elements.findIndex(function (element) { return element.id === original.id; });
                    if (index !== -1) state.elements[index] = moveElement(original, point.x - gesture.start.x, point.y - gesture.start.y);
                });
            } else if (gesture.mode === "resize") {
                var resizedBounds = resizeBounds(gesture.originalBounds, gesture.handle, point.x - gesture.start.x, point.y - gesture.start.y);
                var scaleX = gesture.originalBounds.w ? resizedBounds.w / gesture.originalBounds.w : 1;
                var scaleY = gesture.originalBounds.h ? resizedBounds.h / gesture.originalBounds.h : 1;
                gesture.originals.forEach(function (original) {
                    var originalBox = boundsOf(original);
                    var nextBox = {
                        x: resizedBounds.x + (originalBox.x - gesture.originalBounds.x) * scaleX,
                        y: resizedBounds.y + (originalBox.y - gesture.originalBounds.y) * scaleY,
                        w: originalBox.w * scaleX,
                        h: originalBox.h * scaleY
                    };
                    var resizeIndex = state.elements.findIndex(function (element) { return element.id === original.id; });
                    if (resizeIndex !== -1) state.elements[resizeIndex] = resizeElementTo(original, originalBox, nextBox);
                });
            } else if (gesture.mode === "rotate") {
                var currentAngle = Math.atan2(point.y - gesture.center.y, point.x - gesture.center.x);
                var deltaAngle = currentAngle - gesture.startAngle;
                gesture.originals.forEach(function (original) {
                    var originalBox = boundsOf(original);
                    var elementCenterX = originalBox.x + originalBox.w / 2;
                    var elementCenterY = originalBox.y + originalBox.h / 2;
                    var relativeX = elementCenterX - gesture.center.x;
                    var relativeY = elementCenterY - gesture.center.y;
                    var nextCenterX = gesture.center.x + relativeX * Math.cos(deltaAngle) - relativeY * Math.sin(deltaAngle);
                    var nextCenterY = gesture.center.y + relativeX * Math.sin(deltaAngle) + relativeY * Math.cos(deltaAngle);
                    var rotated = moveElement(original, nextCenterX - elementCenterX, nextCenterY - elementCenterY);
                    rotated.angle = (original.angle || 0) + deltaAngle;
                    var rotateIndex = state.elements.findIndex(function (element) { return element.id === original.id; });
                    if (rotateIndex !== -1) state.elements[rotateIndex] = rotated;
                });
            } else if (gesture.mode === "marquee") {
                state.marquee.x2 = point.x;
                state.marquee.y2 = point.y;
            } else if (gesture.mode === "draw") {
                var element = gesture.element;
                if (element.type === "freedraw") {
                    var last = element.points[element.points.length - 1];
                    if (Math.hypot(point.x - last.x, point.y - last.y) > 1.4) element.points.push(point);
                } else {
                    element.w = point.x - element.x;
                    element.h = point.y - element.y;
                }
            }
            render();
        }

        function pointerUp() {
            if (!gesture) return;
            if (gesture.mode === "draw") {
                var element = gesture.element;
                if (element.type === "freedraw" || Math.hypot(element.w, element.h) > 3) {
                    state.elements.push(element);
                    setSelection([element.id]);
                    saveSnapshot();
                }
            } else if (gesture.mode === "move") {
                saveSnapshot();
            } else if (gesture.mode === "resize") {
                saveSnapshot();
            } else if (gesture.mode === "rotate") {
                saveSnapshot();
            } else if (gesture.mode === "marquee") {
                var marquee = draggedBounds(gesture.start, { x: state.marquee.x2, y: state.marquee.y2 });
                var ids = gesture.baseIds.slice();
                state.elements.forEach(function (element) {
                    if (boxesIntersect(boundsOf(element), marquee) && ids.indexOf(element.id) === -1) ids.push(element.id);
                });
                setSelection(ids);
                state.marquee = null;
            }
            gesture = null;
            state.preview = null;
            canvas.style.cursor = cursorForTool();
            render();
        }

        function cursorForTool() {
            if (state.tool === "hand") return "grab";
            if (state.tool === "selection") return "default";
            if (state.tool === "text") return "text";
            return "crosshair";
        }

        function setTool(tool) {
            state.tool = tool;
            document.querySelectorAll(".tool-button").forEach(function (button) {
                var active = button.id === "tool-" + tool;
                button.classList.toggle("is-active", active);
                button.setAttribute("aria-pressed", active ? "true" : "false");
            });
            canvas.style.cursor = cursorForTool();
            setText("canvas-hint", tool === "selection" ? "Drag to select or move  ·  Space + drag to pan" : tool === "text" ? "Click the canvas to add text" : "Drag to draw  ·  Space + drag to pan");
            render();
            if (tool === "image") byId("image-import").click();
        }

        function setZoom(nextZoom, anchor) {
            var next = Math.max(0.25, Math.min(3, nextZoom));
            var point = anchor || { x: canvas.clientWidth / 2, y: canvas.clientHeight / 2 };
            var sceneX = (point.x - state.panX) / state.zoom;
            var sceneY = (point.y - state.panY) / state.zoom;
            state.zoom = next;
            state.panX = point.x - sceneX * next;
            state.panY = point.y - sceneY * next;
            render();
        }

        function changeSelectedStyle(key, value, commit) {
            if (key === "stroke") state.stroke = value;
            if (key === "fill") state.fill = value;
            if (key === "strokeWidth") state.strokeWidth = value;
            if (key === "strokeStyle") state.strokeStyle = value;
            if (key === "opacity") state.opacity = value;
            if (key === "fontSize") state.fontSize = value;
            selectedElements().forEach(function (element) { element[key] = value; });
            persist();
            if (commit) saveSnapshot();
            render();
        }

        function exportJson() {
            var filename = state.sceneName.trim().replace(/[^a-z0-9_-]+/gi, "-").replace(/^-+|-+$/g, "") || "sketchboard";
            download(new Blob([JSON.stringify(exportSceneData(), null, 2)], { type: "application/json" }), filename + ".excalidraw");
        }

        function exportPng() {
            var bounds = selectionBounds(state.elements) || { x: 0, y: 0, w: 800, h: 600 };
            var padding = 48;
            var scale = Math.min(1, 4096 / Math.max(bounds.w + padding * 2, bounds.h + padding * 2));
            var output = document.createElement("canvas");
            output.width = Math.max(1, Math.ceil((bounds.w + padding * 2) * scale));
            output.height = Math.max(1, Math.ceil((bounds.h + padding * 2) * scale));
            var outputContext = output.getContext("2d");
            outputContext.fillStyle = state.background;
            outputContext.fillRect(0, 0, output.width, output.height);
            var liveContext = context;
            context = outputContext;
            context.save();
            context.setTransform(scale, 0, 0, scale, (padding - bounds.x) * scale, (padding - bounds.y) * scale);
            state.elements.forEach(drawElement);
            context.restore();
            context = liveContext;
            output.toBlob(function (blob) {
                if (blob) download(blob, "sketchboard.png");
            }, "image/png");
        }

        function importJson(file) {
            var reader = new FileReader();
            reader.onload = function () {
                try {
                    var incoming = JSON.parse(String(reader.result));
                    var imported = normalizeScene(incoming);
                    state.elements = imported.elements;
                    state.background = imported.background;
                    state.sceneName = imported.sceneName;
                    state.gridVisible = imported.gridVisible;
                    state.snapToGrid = imported.snapToGrid;
                    state.stroke = imported.stroke;
                    state.fill = imported.fill;
                    state.fillEnabled = imported.fillEnabled;
                    state.strokeWidth = imported.strokeWidth;
                    state.strokeStyle = imported.strokeStyle;
                    state.opacity = imported.opacity;
                    state.fontSize = imported.fontSize;
                    setSelection([]);
                    applyControls();
                    history = [sceneSnapshot()];
                    historyIndex = 0;
                    persist();
                    updateHistoryButtons();
                    render();
                } catch (error) {
                    window.alert("That file is not a supported Sketchboard JSON scene.");
                }
            };
            reader.readAsText(file);
        }

        function undo() {
            if (historyIndex <= 0) return;
            historyIndex -= 1;
            restoreSnapshot(history[historyIndex]);
            persist();
            applyControls();
            updateHistoryButtons();
            render();
        }

        function redo() {
            if (historyIndex >= history.length - 1) return;
            historyIndex += 1;
            restoreSnapshot(history[historyIndex]);
            persist();
            applyControls();
            updateHistoryButtons();
            render();
        }

        document.querySelectorAll(".tool-button").forEach(function (button) {
            button.addEventListener("click", function () { setTool(button.id.replace("tool-", "")); });
        });
        Object.keys(colors).forEach(function (name) {
            var button = byId("stroke-" + name);
            button.addEventListener("click", function () {
                state.stroke = colors[name];
                document.querySelectorAll(".swatch").forEach(function (swatch) { swatch.classList.remove("is-selected"); });
                button.classList.add("is-selected");
                changeSelectedStyle("stroke", state.stroke, true);
            });
        });
        byId("stroke-color").addEventListener("input", function (event) { changeSelectedStyle("stroke", event.target.value, false); });
        byId("stroke-color").addEventListener("change", function (event) { changeSelectedStyle("stroke", event.target.value, true); });
        byId("fill-color").addEventListener("input", function (event) { state.fillEnabled = true; changeSelectedStyle("fill", event.target.value, false); });
        byId("fill-color").addEventListener("change", function (event) { changeSelectedStyle("fill", event.target.value, true); });
        byId("fill-toggle").addEventListener("click", function () {
            state.fillEnabled = !state.fillEnabled;
            byId("fill-toggle").textContent = state.fillEnabled ? "Fill on" : "No fill";
            byId("fill-toggle").setAttribute("aria-pressed", state.fillEnabled ? "true" : "false");
            selectedElements().forEach(function (element) { element.fill = state.fillEnabled ? state.fill : "transparent"; });
            persist();
            saveSnapshot();
            render();
        });
        byId("stroke-width").addEventListener("input", function (event) { changeSelectedStyle("strokeWidth", Number(event.target.value), false); });
        byId("stroke-width").addEventListener("change", function (event) { changeSelectedStyle("strokeWidth", Number(event.target.value), true); });
        byId("element-opacity").addEventListener("input", function (event) { changeSelectedStyle("opacity", Number(event.target.value) / 100, false); });
        byId("element-opacity").addEventListener("change", function (event) { changeSelectedStyle("opacity", Number(event.target.value) / 100, true); });
        byId("font-size").addEventListener("input", function (event) { changeSelectedStyle("fontSize", Number(event.target.value), false); });
        byId("font-size").addEventListener("change", function (event) { changeSelectedStyle("fontSize", Number(event.target.value), true); });
        byId("line-style").addEventListener("change", function (event) { changeSelectedStyle("strokeStyle", event.target.value, true); });
        byId("background-color").addEventListener("input", function (event) { state.background = event.target.value; persist(); render(); });
        byId("background-color").addEventListener("change", function (event) { state.background = event.target.value; persist(); saveSnapshot(); render(); });
        byId("snap-toggle").addEventListener("click", function () { state.snapToGrid = !state.snapToGrid; applyControls(); persist(); saveSnapshot(); render(); });
        byId("grid-toggle").addEventListener("click", function () { state.gridVisible = !state.gridVisible; applyControls(); persist(); saveSnapshot(); render(); });
        byId("undo").addEventListener("click", undo);
        byId("redo").addEventListener("click", redo);
        byId("zoom-in").addEventListener("click", function () { setZoom(state.zoom * 1.2); });
        byId("zoom-out").addEventListener("click", function () { setZoom(state.zoom / 1.2); });
        byId("zoom-fit").addEventListener("click", fitAll);
        byId("delete-selection").addEventListener("click", deleteSelection);
        byId("duplicate-selection").addEventListener("click", duplicateSelection);
        byId("group-selection").addEventListener("click", groupSelection);
        byId("ungroup-selection").addEventListener("click", ungroupSelection);
        byId("send-backward").addEventListener("click", function () { reorderSelection(-1); });
        byId("bring-forward").addEventListener("click", function () { reorderSelection(1); });
        byId("clear-scene").addEventListener("click", function () {
            if (!state.elements.length || !window.confirm("Start a new empty board?")) return;
            state.elements = [];
            setSelection([]);
            state.panX = 0;
            state.panY = 0;
            state.zoom = 1;
            saveSnapshot();
            render();
        });
        byId("export-json").addEventListener("click", exportJson);
        byId("export-png").addEventListener("click", exportPng);
        byId("open-json").addEventListener("click", function () { byId("scene-import").click(); });
        byId("scene-import").addEventListener("change", function (event) {
            if (event.target.files && event.target.files[0]) importJson(event.target.files[0]);
            event.target.value = "";
        });
        byId("image-import").addEventListener("change", function (event) {
            if (event.target.files && event.target.files[0]) importImage(event.target.files[0]);
            event.target.value = "";
        });

        canvas.addEventListener("pointerdown", pointerDown);
        canvas.addEventListener("pointermove", pointerMove);
        canvas.addEventListener("pointerup", pointerUp);
        canvas.addEventListener("pointercancel", pointerUp);
        canvas.addEventListener("wheel", function (event) {
            event.preventDefault();
            var anchor = viewportPoint(event);
            setZoom(state.zoom * (event.deltaY < 0 ? 1.08 : 0.92), anchor);
        }, { passive: false });
        window.addEventListener("keydown", function (event) {
            var target = event.target;
            if (target && ["INPUT", "TEXTAREA", "SELECT"].indexOf(target.tagName) !== -1) return;
            if (event.code === "Space") { spaceDown = true; event.preventDefault(); }
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "z") {
                event.preventDefault();
                if (event.shiftKey) redo(); else undo();
                return;
            }
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "y") { event.preventDefault(); redo(); return; }
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "a") {
                event.preventDefault();
                setSelection(state.elements.map(function (element) { return element.id; }));
                render();
                return;
            }
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "c") { event.preventDefault(); copySelection(); return; }
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "v") { event.preventDefault(); pasteClipboard(); return; }
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "d") { event.preventDefault(); duplicateSelection(); return; }
            if (event.key === "Home") { event.preventDefault(); fitAll(); return; }
            if (event.key === "Escape") { setSelection([]); state.marquee = null; render(); return; }
            if ((event.key === "Backspace" || event.key === "Delete") && state.selectedIds.length) {
                deleteSelection();
                return;
            }
            var shortcuts = { v: "selection", h: "hand", r: "rectangle", d: "diamond", o: "ellipse", a: "arrow", l: "line", p: "freedraw", t: "text", e: "eraser" };
            if (shortcuts[event.key.toLowerCase()]) setTool(shortcuts[event.key.toLowerCase()]);
        });
        window.addEventListener("keyup", function (event) { if (event.code === "Space") spaceDown = false; });
        window.addEventListener("blur", function () { spaceDown = false; });
        if (window.ResizeObserver) new ResizeObserver(resizeCanvas).observe(host);
        else window.addEventListener("resize", resizeCanvas);

        history = [sceneSnapshot()];
        historyIndex = 0;
        loadSaved();
        applyControls();
        updateHistoryButtons();
        setTool("selection");
        resizeCanvas();
    }

    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", startSketchboard, { once: true });
    else startSketchboard();
})();
</script>"""


#include <expapilib.ARKlight>
