import threeStatementAnalysisJson from "./three-statement-analysis.json";

export type ForecastPoint = {
  year: string;
  revenue: number;
  npat: number;
  grossMargin: number;
  status: "management_lfl_actual" | "management_projection";
  basis: string;
  sourceId: "DMX_IPO_PRESENTATION_2026";
};

export const dataCutoff = "13 July 2026";

export const ipoFacts = {
  offerPriceVnd: 80_000,
  sharesIssuedMillion: 166.4385,
  postOfferSharesMillion: 1_267.722,
  grossProceedsVndBn: 13_315.08,
  mwgOwnershipDisclosure: "nearly 86%",
  // Used only in illustrative calculations; no exact percentage was disclosed.
  mwgOwnershipModelApproxPct: 86.0,
  postMoneyEquityVndBn: 101_417.76,
  sourceId: "DMX_IPO_RESULT_2026",
  asOf: "30 June 2026",
  status: "official transaction result",
  basis: "completed primary offering",
};

export const q1Facts = {
  revenue2026VndBn: 32_541.95,
  revenue2025VndBn: 25_153.56,
  grossProfit2026VndBn: 6_241.22,
  grossProfit2025VndBn: 4_526.17,
  npat2026VndBn: 2_218.57,
  npat2025VndBn: 1_478.38,
  cfo2026VndBn: 863.69,
  cfo2025VndBn: 2_477.05,
  inventoryNetVndBn: 23_054.45,
  inventoryProvisionVndBn: -749.03,
  cashVndBn: 3_312.68,
  termDepositsVndBn: 26_755.21,
  shortTermDebtVndBn: 22_158.89,
  sourceId: "DMX_DATA_2026Q1",
  asOf: "31 March 2026",
  status: "official unaudited consolidated financials",
  basis: "reported",
};

export const sixMonthFacts = {
  revenueVndBn: 65_279,
  revenueGrowthPct: 31,
  sameStoreSalesGrowthPct: 32,
  revenueGuidanceCompletionPct: 53,
  erablueStores: 261,
  erablueRevenueGrowthPct: 92,
  financedSalesMixPct: 38,
  sourceId: "DMX_RESULTS_2026H1",
  asOf: "30 June 2026",
  status: "issuer operating update; unaudited",
  basis: "issuer-stated like-for-like operating update",
  revenueGrowthBasis: "stated like-for-like basis",
};

export const managementForecast: ForecastPoint[] = [
  {
    year: "2025A",
    revenue: 107_000,
    npat: 6_075,
    grossMargin: 17.1,
    status: "management_lfl_actual",
    basis: "management-adjusted like-for-like actual",
    sourceId: "DMX_IPO_PRESENTATION_2026",
  },
  {
    year: "2026F",
    revenue: 122_500,
    npat: 7_350,
    grossMargin: 17.5,
    status: "management_projection",
    basis: "management projection",
    sourceId: "DMX_IPO_PRESENTATION_2026",
  },
  {
    year: "2027F",
    revenue: 135_000,
    npat: 8_500,
    grossMargin: 17.8,
    status: "management_projection",
    basis: "management projection",
    sourceId: "DMX_IPO_PRESENTATION_2026",
  },
  {
    year: "2028F",
    revenue: 149_000,
    npat: 9_800,
    grossMargin: 18.0,
    status: "management_projection",
    basis: "management projection",
    sourceId: "DMX_IPO_PRESENTATION_2026",
  },
  {
    year: "2029F",
    revenue: 164_000,
    npat: 11_300,
    grossMargin: 18.3,
    status: "management_projection",
    basis: "management projection",
    sourceId: "DMX_IPO_PRESENTATION_2026",
  },
  {
    year: "2030F",
    revenue: 182_000,
    npat: 13_000,
    grossMargin: 18.4,
    status: "management_projection",
    basis: "management projection",
    sourceId: "DMX_IPO_PRESENTATION_2026",
  },
];

export const officialSources = [
  {
    id: "DMX_IPO_RESULT_2026",
    title: "DMX board resolution approving the IPO result",
    detail: "Official offer result, proceeds and post-offer share bridge",
    url: "https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/7/0/f1/08/f108ca2a7399d9a70674915a4b2cf651.pdf",
  },
  {
    id: "DMX_DATA_2026Q1",
    title: "DMX official Q1 2026 financial data pack",
    detail: "Allowlisted balance sheet, income statement and cash-flow facts",
    url: "https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/6/0/6b/e5/6be50a510e272451464dae07771401ca.xlsx",
  },
  {
    id: "DMX_RESULTS_2026H1",
    title: "DMX business results — six months 2026",
    detail: "Unaudited operating update, LFL revenue, store network and KPIs",
    url: "https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/7/5006021/b5/ee/b5ee17c283b469b12b3b435d00da8aa4.pdf",
  },
  {
    id: "DMX_IPO_PRESENTATION_2026",
    title: "DMX IPO presentation",
    detail: "Management 2026–2030 outlook and model boundary",
    url: "https://cdnv2-tmdt.tgdd.vn/mwgvn/investorrelations/files/posts/2026/6/5005889/4a/f4/4af4a4152a74661a28063a23b4d6747f.pdf",
  },
  {
    id: "MWG_AR_2025",
    title: "MWG Annual Report 2025",
    detail: "Group structure, historical financials and governance",
    url: "https://cdnv2.tgdd.vn/mwgvn/investorrelations/files/posts/2026/3/5677/48/8a/488ab752e1224bcbd9dd5413be04179f.pdf",
  },
];

export const modelBoundary = {
  insideDmx: [
    "The Gioi Di Dong",
    "Dien May Xanh",
    "TopZone",
    "DMX Technician",
    "EraBlue joint venture",
    "Consumer-finance and utility touchpoints",
  ],
  mwgStub: [
    "Bach Hoa Xanh",
    "An Khang",
    "AvaKids",
    "Corporate and other assets",
  ],
};

export const analyticalChecks = [
  "Reported and like-for-like figures are stored separately.",
  "EraBlue is valued inside DMX only; it is never added again to the MWG stub.",
  "IPO proceeds enter the post-money valuation and cash bridge once.",
  "Financial-statement extraction allowlists BS, IS and CF sheets only.",
  "Every official fact group carries a source ID, status, basis and as-of date.",
  "Scenario assumptions are labelled as analyst inputs, never as company guidance.",
];

/**
 * Generated by scripts/build_three_statement_analysis.py. Keeping the import
 * here gives every React presentation component one typed, versioned payload
 * instead of duplicating historical figures in JSX.
 */
export const threeStatementAnalysis = threeStatementAnalysisJson;
