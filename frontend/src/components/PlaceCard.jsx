/* src/styles/ficha.css */

.aa-ficha {
  background: #0f172a;
  color: #f8fafc;
  padding: 2rem;
  font-family: "Inter", system-ui, sans-serif;
}

.aa-ficha-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.aa-breadcrumbs {
  display: flex;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.aa-breadcrumbs span:not(:last-child)::after {
  content: "›";
  margin-left: 0.5rem;
}

.aa-close {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 1.5rem;
  cursor: pointer;
}

.aa-score-header {
  display: flex;
  align-items: baseline;
  gap: 1rem;
  margin-bottom: 2rem;
}

.aa-score-num {
  font-size: 4rem;
  font-weight: 700;
  color: #f8fafc;
}

.aa-score-text {
  font-size: 1.25rem;
  font-weight: 600;
}

.aa-score-sub {
  font-size: 0.875rem;
  color: #94a3b8;
}

.aa-ficha-body {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.aa-compare {
  position: relative;
  aspect-ratio: 1;
  overflow: hidden;
  border-radius: 8px;
}

.aa-compare-imgs {
  position: relative;
  width: 100%;
  height: 100%;
}

.aa-compare-base,
.aa-compare-top {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.aa-compare-handle {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #f8fafc;
  transform: translateX(-50%);
}

.aa-handle-circle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 40px;
  height: 40px;
  background: #f8fafc;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #0f172a;
  font-weight: 700;
}

.aa-compare-labels {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #f8fafc;
  background: rgba(0, 0, 0, 0.5);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.aa-compare-corners {
  position: absolute;
  bottom: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #f8fafc;
  background: rgba(0, 0, 0, 0.5);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.aa-compare-slider {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: ew-resize;
}

.aa-bars-section h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: #f8fafc;
}

.aa-bar-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.aa-bar-label {
  flex: 1;
  font-size: 0.875rem;
  color: #cbd5e1;
}

.aa-bar-track {
  width: 120px;
  height: 8px;
  background: #1e293b;
  border-radius: 4px;
  overflow: hidden;
}

.aa-bar-fill {
  height: 100%;
  background: #06b6d4;
  border-radius: 4px;
}

.aa-bar-value {
  width: 40px;
  text-align: right;
  font-size: 0.875rem;
  color: #f8fafc;
  font-variant-numeric: tabular-nums;
}

.aa-matches-breaks {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 2rem;
}

.aa-matches h3,
.aa-breaks h3 {
  font-size: 1rem;
  margin-bottom: 1rem;
  color: #f8fafc;
}

.aa-match-row,
.aa-break-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #1e293b;
  font-size: 0.875rem;
}

.aa-break-value {
  font-weight: 700;
  color: #f8fafc;
}

.aa-limites {
  margin-bottom: 2rem;
}

.aa-limites h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #f8fafc;
}

.aa-limites-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.aa-limite-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #1e293b;
  font-size: 0.875rem;
}

.aa-limite-label {
  color: #cbd5e1;
}

.aa-limite-mars {
  color: #f8fafc;
  font-weight: 600;
}

.aa-limite-earth {
  color: #94a3b8;
}

.aa-fuentes {
  font-size: 0.75rem;
  color: #64748b;
  margin-bottom: 1.5rem;
}

.aa-actions {
  display: flex;
  gap: 1rem;
}

.aa-actions button {
  background: #1e293b;
  color: #f8fafc;
  border: 1px solid #334155;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.875rem;
}

.aa-actions button:hover {
  background: #334155;
}
