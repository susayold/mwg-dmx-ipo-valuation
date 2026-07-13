"use client";

import { useMemo, useState } from "react";
import { ipoFacts } from "../data/case-data";

type ScenarioName = "Bear" | "Base" | "Bull";

type Scenario = {
  npat: number;
  pe: number;
  stubValue: number;
  parentAdjustments: number;
  mwgShares: number;
  referencePrice: number;
};

const scenarios: Record<ScenarioName, Scenario> = {
  Bear: {
    npat: 6_700,
    pe: 10,
    stubValue: 28_000,
    parentAdjustments: -8_000,
    mwgShares: 1_400,
    referencePrice: 100_000,
  },
  Base: {
    npat: 7_350,
    pe: 12.3,
    stubValue: 45_000,
    parentAdjustments: -5_000,
    mwgShares: 1_400,
    referencePrice: 100_000,
  },
  Bull: {
    npat: 8_000,
    pe: 14,
    stubValue: 65_000,
    parentAdjustments: -3_000,
    mwgShares: 1_400,
    referencePrice: 100_000,
  },
};

const formatBn = (value: number) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value);

const formatVnd = (value: number) =>
  new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
    maximumFractionDigits: 0,
  }).format(value);

function RangeInput({
  label,
  value,
  min,
  max,
  step,
  suffix,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  suffix: string;
  onChange: (value: number) => void;
}) {
  return (
    <label className="lab-control">
      <span>
        {label}
        <strong>
          {formatBn(value)}
          {suffix}
        </strong>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(event) => onChange(Number(event.target.value))}
      />
    </label>
  );
}

export function ValuationLab() {
  const [activeScenario, setActiveScenario] = useState<ScenarioName>("Base");
  const [inputs, setInputs] = useState<Scenario>(scenarios.Base);

  const output = useMemo(() => {
    const dmxEquity = inputs.npat * inputs.pe;
    const mwgDmxStake =
      dmxEquity * (ipoFacts.mwgOwnershipModelApproxPct / 100);
    const mwgEquity = mwgDmxStake + inputs.stubValue + inputs.parentAdjustments;
    const impliedValuePerShare = (mwgEquity / inputs.mwgShares) * 1_000;
    const premiumDiscount =
      inputs.referencePrice === 0
        ? 0
        : impliedValuePerShare / inputs.referencePrice - 1;

    return {
      dmxEquity,
      mwgDmxStake,
      mwgEquity,
      impliedValuePerShare,
      premiumDiscount,
    };
  }, [inputs]);

  const applyScenario = (name: ScenarioName) => {
    setActiveScenario(name);
    setInputs(scenarios[name]);
  };

  const update = (key: keyof Scenario, value: number) => {
    setActiveScenario("Base");
    setInputs((current) => ({ ...current, [key]: value }));
  };

  return (
    <div className="valuation-lab">
      <div className="lab-head">
        <div>
          <span className="eyebrow dark">Interactive model</span>
          <h3>Rebuild the SOTP in under a minute.</h3>
          <p>
            Change the earnings anchor, multiple and stub value. All figures
            below are analyst scenarios—not company guidance or a recommendation.
          </p>
        </div>
        <div className="scenario-tabs" aria-label="Valuation scenarios">
          {(Object.keys(scenarios) as ScenarioName[]).map((name) => (
            <button
              type="button"
              key={name}
              className={activeScenario === name ? "active" : ""}
              onClick={() => applyScenario(name)}
            >
              {name}
            </button>
          ))}
        </div>
      </div>

      <div className="lab-grid">
        <div className="lab-inputs">
          <RangeInput
            label="DMX 2026E NPAT"
            value={inputs.npat}
            min={5_500}
            max={9_000}
            step={50}
            suffix=" bn"
            onChange={(value) => update("npat", value)}
          />
          <RangeInput
            label="DMX forward P/E"
            value={inputs.pe}
            min={8}
            max={18}
            step={0.1}
            suffix="×"
            onChange={(value) => update("pe", value)}
          />
          <RangeInput
            label="Non-DMX stub value"
            value={inputs.stubValue}
            min={10_000}
            max={90_000}
            step={1_000}
            suffix=" bn"
            onChange={(value) => update("stubValue", value)}
          />
          <RangeInput
            label="Parent adjustments"
            value={inputs.parentAdjustments}
            min={-15_000}
            max={5_000}
            step={500}
            suffix=" bn"
            onChange={(value) => update("parentAdjustments", value)}
          />
          <RangeInput
            label="MWG diluted shares"
            value={inputs.mwgShares}
            min={1_300}
            max={1_500}
            step={1}
            suffix=" m"
            onChange={(value) => update("mwgShares", value)}
          />
          <RangeInput
            label="Your reference price"
            value={inputs.referencePrice}
            min={40_000}
            max={220_000}
            step={1_000}
            suffix=""
            onChange={(value) => update("referencePrice", value)}
          />
        </div>

        <div className="lab-output">
          <span className="output-label">Illustrative MWG value / share</span>
          <strong className="output-value">
            {formatVnd(output.impliedValuePerShare)}
          </strong>
          <span
            className={[
              "premium",
              output.premiumDiscount >= 0 ? "positive" : "negative",
            ].join(" ")}
          >
            {output.premiumDiscount >= 0 ? "+" : ""}
            {(output.premiumDiscount * 100).toFixed(1)}% vs your reference
          </span>

          <div className="value-bridge">
            <div>
              <span>DMX equity value</span>
              <strong>{formatBn(output.dmxEquity)} bn</strong>
            </div>
            <div>
              <span>MWG share of DMX (~86% model approximation)</span>
              <strong>{formatBn(output.mwgDmxStake)} bn</strong>
            </div>
            <div>
              <span>Non-DMX stub</span>
              <strong>{formatBn(inputs.stubValue)} bn</strong>
            </div>
            <div>
              <span>Parent adjustments</span>
              <strong>{formatBn(inputs.parentAdjustments)} bn</strong>
            </div>
            <div className="total">
              <span>MWG equity value</span>
              <strong>{formatBn(output.mwgEquity)} bn</strong>
            </div>
          </div>

          <p className="lab-note">
            The default share count and stub values are transparent model inputs.
            Replace them with your own cut-off-date assumptions before using the
            output.
          </p>
        </div>
      </div>
    </div>
  );
}
