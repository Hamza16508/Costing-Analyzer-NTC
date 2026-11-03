// Builds docs/phase0/questionnaire/NTC-PO-Questionnaire.docx (Phase 0, design artefact).
// Usage: node scripts/build_po_questionnaire.js <out.docx>
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
  AlignmentType, HeadingLevel, BorderStyle, Footer, PageNumber, LevelFormat,
} = require("docx");

const FONT = "Arial";
const ACC = "0B6A73";
const LIGHT = "E3F0F0";
const GREY = "F3F5F5";
const W = 9638; // A4 text width at 2 cm margins (DXA)

const run = (text, o = {}) => new TextRun({ text, font: FONT, size: 20, ...o });
const p = (children, o = {}) => new Paragraph({ children: Array.isArray(children) ? children : [run(children)], spacing: { after: 100 }, ...o });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const bullet = (t) => new Paragraph({ numbering: { reference: "b", level: 0 }, children: Array.isArray(t) ? t : [run(t)], spacing: { after: 60 } });
const border = { style: BorderStyle.SINGLE, size: 4, color: "B8C4C4" };
const borders = { top: border, bottom: border, left: border, right: border };

function cell(content, width, o = {}) {
  const kids = (Array.isArray(content) ? content : [content]).map((c) => (typeof c === "string" ? p([run(c, o.run || {})], { spacing: { after: 40 } }) : c));
  return new TableCell({
    children: kids, width: { size: width, type: WidthType.DXA }, borders,
    shading: o.fill ? { type: ShadingType.CLEAR, color: "auto", fill: o.fill } : undefined,
    margins: { top: 80, bottom: 80, left: 110, right: 110 }, columnSpan: o.span,
  });
}
function table(widths, rows) {
  return new Table({ width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: widths, rows });
}
function headerRow(widths, labels) {
  return new TableRow({ cantSplit: true, tableHeader: true, children: labels.map((l, i) => cell(l, widths[i], { fill: LIGHT, run: { bold: true } })) });
}
const blank = (n = 1) => Array.from({ length: n }, () => p([run(" ")], { spacing: { after: 40 } }));
const space = () => new Paragraph({ children: [], spacing: { after: 120 } });

// ---------- content ----------
const known = [
  "The export is Sheet1 of “Nylon Tyre Cord.xls.xlsx” (the copy attached on 3 Nov 2026, identical to the one analysed): 1,989 delivery lines (organisation TYR) from 19 Oct 2016 to 24 Oct 2026.",
  "PO_UNIT_PRICE is the landed cost in PKR per kg (confirmed by Hamza on 3 Nov 2026), and Q_VALUE = quantity × price on every line.",
  "Receipt 132135 (1 PKR/kg on 12 Mar 2025) is a provisional entry; the Service Long March zero-price lines are intercompany transfers; Hanif receipt 28753 and the 956,415,064 PKR/kg Burlytex line are excluded.",
  "Material is classified by the cord construction written in the description (840D/2, 1260D/2, 840D/1, 1890D/2, 1260D/1, chafer). CLOTH and TEXTILE lines are left out.",
  "The bank’s USD/PKR rates for LC payments, the FOB-versus-CFR freight comparison and the mill country of each trader have been requested separately; Parts F and G below are where you can supply them.",
];

const mcqs = [
  { q: "When is the price on a purchase order line fixed?",
    why: "This tells us which date’s market prices explain the price you paid.",
    o: ["When the PO or contract is signed", "When the LC is opened", "When the goods are shipped (bill of lading date)", "Only at receipt, when the landed cost is worked out"] },
  { q: "How is the supplier’s price normally agreed?",
    why: "Spot prices follow the market quickly; contract or formula prices follow it with a delay.",
    o: ["Negotiated for each order at the current market price", "A fixed price for a period (monthly, quarterly or yearly contract)", "A formula linked to an index, such as caprolactam or nylon chip prices", "It differs by supplier (name which supplier uses which method under E)"] },
  { q: "Which exchange rate turns the supplier’s foreign-currency price into the PKR figure in PO_UNIT_PRICE?",
    why: "We must use the same rate when we convert prices back to USD.",
    o: ["The bank rate on the day the LC or bill is paid (retired)", "The customs rate on the goods declaration (GD) date", "The rate on the PO date", "A standard or budget rate, adjusted later"] },
  { q: "In which currency do import suppliers invoice you?",
    why: "This decides whether movements in the Chinese yuan reach your price directly.",
    o: ["Always US dollars", "Mostly US dollars, some in Chinese yuan", "Mostly Chinese yuan", "Another mix (please name it under E)"] },
  { q: "After a delivery line is first entered, can its PO_UNIT_PRICE change?",
    why: "We need to know whether the price we see is final, and how corrections appear in the export.",
    o: ["No; the price is final when the line is entered", "Yes; it is entered as provisional and corrected later on the same line", "Corrections are posted as new lines or receipts (as with receipt 132135)", "Corrections are made outside this report (for example in the general ledger), so the export is never updated"] },
  { q: "FREIGHT_CHARGES holds a PKR amount per receipt (765 lines, mostly imports). How does it relate to PO_UNIT_PRICE?",
    why: "If it is already inside the landed cost and we add it again, freight is counted twice.",
    o: ["It is already included in PO_UNIT_PRICE", "It is paid separately and is not included in PO_UNIT_PRICE", "It is included for local purchases only", "It varies from receipt to receipt (explain under E)"] },
  { q: "Within one construction (for example 840D/2), does the price change with EPI (ends per inch) or fabric width?",
    why: "If EPI or width moves the price per kg, we must compare like with like.",
    o: ["No; denier and ply set the price per kg, and EPI or width make no real difference", "Yes, EPI changes the price per kg", "Yes, width changes the price per kg", "Both EPI and width change the price per kg"] },
  { q: "Which customs duty treatment applies to your nylon tyre cord imports (PCT 5902.1000)?",
    why: "Duties are part of landed cost, so a change in the duty rate moves your price.",
    o: ["Normal duties on every shipment", "A concession or exemption (SRO, export scheme) on some shipments", "A concession or exemption on most shipments", "The treatment changed over the years (list the changes and dates in Part G)"] },
  { q: "Why does the company sometimes buy cord from other tyre makers (Diamond, Crown, Ghauri) and local stockists (MB & Company, Qaisar Traders and others)?",
    why: "This tells us whether these prices are comparable to your import prices.",
    o: ["Emergency purchases at the local market price", "Borrowing or exchange, returned in kind later", "Their surplus stock, bought at a discount", "A mix of these (explain under E)"] },
  { q: "Does this export contain every nylon tyre cord receipt from Oct 2016 to Oct 2026?",
    why: "Missing receipts or returns would distort volumes and averages.",
    o: ["Yes, it is complete", "No; some receipts are booked under other organisation codes or sites", "No; returns or rejections are not shown and should be netted off", "No; some periods are missing (for example after a system change)"] },
];

const shortQs = [
  "On average, how many days pass between the PO or contract date and the delivery date (TRANSACTION_DATE), for imports and for local purchases?",
  "Which delivery term do you mostly buy on (FOB, CFR or CIF), and has this changed over the years?",
  "Do payment terms (Sight, CAD, 60 or 90 days) change the price you pay, and are LC or bank charges and interest included in PO_UNIT_PRICE?",
  "After delivery, are there quality claims, rebates or debit notes that lower the price you actually paid, and where are they recorded?",
  "Did the ERP system, the costing method or the way POs are entered change at any time between 2016 and 2026, and if so, when?",
];

const costParts = [
  "Supplier price (FOB)", "Sea freight", "Marine insurance", "Customs duty (CD, ACD, RD)", "Sales tax (adjustable)",
  "Income tax withheld at import", "Port, terminal and shipping-line charges", "Clearing agent fees", "Bank and LC charges",
  "Exchange gain or loss", "Inland freight to the factory", "Other (please name)",
];

const fields = [
  ["TRANSACTION_DATE", "The date the goods were received into the store (GRN date)."],
  ["VENDOR_SITE: IMPORTS, IMPORTS(CAD), IMPORTS(LC)", "How the import is paid: IMPORTS(CAD) by cash against documents, IMPORTS(LC) by letter of credit; plain IMPORTS covers both."],
  ["SUBINVENTORY: ATT, CTT, LOAN", "The store that received the goods; LOAN (1 line) is stock borrowed or lent."],
  ["PARTY_REFERNCE: CASH, EFS", "How the transporter or local supplier was paid (cash, or EFS = electronic funds)."],
  ["LC_NUMBER blank (163 lines)", "No LC was used (local purchase, CAD or advance payment)."],
  ["BILTY_NO and VEHICLE_NUM", "The truck bilty and vehicle that delivered the goods from port or supplier to the factory."],
  ["Several prices on one PO and item (169 of 1,390 PO-item pairs; the gap is usually 1\u20133%, but up to 61%, between shipments up to 395 days apart)", "Each shipment under the same PO gets its own landed cost (different exchange rate, freight or duties); the supplier price itself is the same."],
  ["One LC_NUMBER on several POs (110 of 395 LCs)", "One letter of credit can cover several POs from the same supplier."],
  ["BILTY_NO with several numbers joined by + (41 lines, e.g. 8452+8479+8289+10729)", "One receipt was delivered by several trucks."],
];

const lines = [
  ["Receipt 75257, 24 Mar 2021", "Two identical lines: item 102-TX02169, 1,944 kg each at 787.69 PKR/kg.", ["Two real deliveries", "Entered twice by mistake"]],
  ["Receipt 146081, 29 Jan 2026", "Two identical lines: item 102-TX01879, 9,862.5 kg each at 637.06 PKR/kg.", ["Two real deliveries", "Entered twice by mistake"]],
  ["Dec 2018 and Jul 2020", "No nylon cord deliveries at all in these two months.", ["Correct, nothing was received", "Deliveries are missing from the export"]],
  ["Receipts 89481, 152651, 153935, 156822, 158578 (2022\u20132026)", "The same item has two different prices inside one receipt (e.g. 152651: 629.47 and 687.00 PKR/kg).", ["Two shipments costed separately", "One price is provisional and not yet final"]],
  ["16 import lines with whole-number prices (8 of them in 2026, e.g. Weifang Kelida 650.00 in Apr 2026, Jiangsu Haohui 800.00 in Sep 2026)", "Every other import line has a costed price with decimals.", ["Provisional prices, still to be replaced by the final landed cost", "Final prices that happen to be round"]],
  ["Receipt 41304, 27 Aug 2018", "Items 102-TX01150 and 102-TX01305 carry each other’s description (840D/2 and 1890D/2).", ["The description is right (we use it)", "The item code is right"]],
];

const vendors = [
  ["GPS London Ltd., UK", "91 lines, 2016–2022"],
  ["G.T. Trading Co., Ltd., Thailand", "85 lines, 2016–2020"],
  ["Yusheng Enterprise Ltd., Hong Kong", "61 lines, 2019–2023 (a brochure points to Weifang, China)"],
  ["Burlytex Group Ltd., Dubai", "36 lines, 2016–2024"],
  ["Stalwart Group DMCC, Dubai", "15 lines, 2021"],
  ["Altek International FZE, Dubai", "4 lines, 2021"],
  ["HL Group Ltd", "8 lines, 2022–2024"],
  ["Crypto Trade Ltd., Seychelles", "1 line, 2021"],
  ["Jiangsu Haohui Trading (China)", "565 lines, 2018–2026"],
  ["Ningbo Jinlun Import & Export (China)", "155 lines, 2016–2025"],
];

const docsToAttach = [
  "One complete landed-cost sheet for a typical import shipment from China, showing every cost component (this is the most useful single document).",
  "The bank’s USD/PKR rates applied to your LC and CAD payments since 2016 (statement or spreadsheet).",
  "Your FOB-versus-CFR comparison for China purchases, and any freight invoices or forwarder quotes.",
  "A list of customs duty rates, SROs or exemptions used for PCT 5902.1000, with the dates they applied.",
  "One sample supply contract or price agreement with a main supplier (for example Jiangsu Haohui or Weifang Kelida).",
];

// ---------- build ----------
const kids = [];
kids.push(new Paragraph({ children: [new TextRun({ text: "Nylon Tyre Cord Purchase Orders", font: FONT, size: 40, bold: true, color: ACC })], spacing: { after: 60 } }));
kids.push(new Paragraph({ children: [new TextRun({ text: "Questionnaire for the commercial specialist", font: FONT, size: 28, color: "333333" })], spacing: { after: 240 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACC, space: 6 } } }));
kids.push(p([run("Why we ask. ", { bold: true }), run("We are building a tool that explains, for every nylon tyre cord purchase since 2016, how much of the price came from raw materials, freight, exchange rates and world events. To do that correctly we must understand exactly how your purchase order data is recorded. This is the only questionnaire about the PO data, so please answer every item.")]));
kids.push(p([run("How to fill it in. ", { bold: true }), run("Tick one box per multiple-choice question (☒ or X); use E to write your own answer if none fits. Write one sentence for each short question. Where you are unsure, say so rather than guess. It should take about 30–40 minutes. Save the filled file and send it back with any documents from Part G.")]));
kids.push(space());
kids.push(table([2400, 7238], [
  new TableRow({ cantSplit: true, children: [cell("Name", 2400, { fill: GREY, run: { bold: true } }), cell(" ", 7238)] }),
  new TableRow({ cantSplit: true, children: [cell("Role", 2400, { fill: GREY, run: { bold: true } }), cell(" ", 7238)] }),
  new TableRow({ cantSplit: true, children: [cell("Date", 2400, { fill: GREY, run: { bold: true } }), cell(" ", 7238)] }),
]));
kids.push(space());
kids.push(h2("Already settled (no need to answer)"));
known.forEach((k) => kids.push(bullet(k)));

kids.push(h1("Part A. Multiple-choice questions"));
mcqs.forEach((m, i) => {
  const rows = [new TableRow({ cantSplit: true, children: [cell([p([run(`A${i + 1}. `, { bold: true, color: ACC }), run(m.q, { bold: true })], { spacing: { after: 40 } }),
    p([run(m.why, { italics: true, color: "5D6B70", size: 18 })], { spacing: { after: 0 } })], W, { fill: LIGHT, span: 2 })] })];
  "ABCD".split("").forEach((L, j) => rows.push(new TableRow({ cantSplit: true, children: [cell(`☐  ${L}`, 900, { run: { bold: true } }), cell(m.o[j], W - 900)] })));
  rows.push(new TableRow({ cantSplit: true, children: [cell("☐  E", 900, { run: { bold: true } }), cell([p([run("Other (please write): ", { color: "5D6B70" })], { spacing: { after: 40 } }), ...blank(1)], W - 900)] }));
  kids.push(table([900, W - 900], rows));
  kids.push(space());
});

kids.push(h1("Part B. Short questions (one sentence each)"));
shortQs.forEach((q, i) => {
  kids.push(table([W], [
    new TableRow({ cantSplit: true, children: [cell([p([run(`B${i + 1}. `, { bold: true, color: ACC }), run(q, { bold: true })], { spacing: { after: 0 } })], W, { fill: LIGHT })] }),
    new TableRow({ cantSplit: true, children: [cell(blank(2), W)] }),
  ]));
  kids.push(space());
});

kids.push(h1("Part C. What is inside PO_UNIT_PRICE"));
kids.push(p("For each cost item, tick whether it is included in the landed cost recorded in PO_UNIT_PRICE. If you know its usual share of the landed cost, write it as a percentage (optional)."));
const cw = [3000, 800, 800, 1400, 1400, 2238];
kids.push(table(cw, [headerRow(cw, ["Cost item", "Yes", "No", "Sometimes", "Usual share %", "Notes"]),
  ...costParts.map((c) => new TableRow({ cantSplit: true, children: [cell(c, cw[0]), cell("☐", cw[1]), cell("☐", cw[2]), cell("☐", cw[3]), cell(" ", cw[4]), cell(" ", cw[5])] }))]));

kids.push(h1("Part D. Field meanings: is our reading right?"));
kids.push(p("This is how we currently read these columns. Tick Correct, or write the correct meaning."));
const fw = [2600, 3538, 1400, 2100];
kids.push(table(fw, [headerRow(fw, ["Column or pattern", "Our reading", "Correct?", "If not, the correct meaning"]),
  ...fields.map(([f, r]) => new TableRow({ cantSplit: true, children: [cell(f, fw[0], { run: { bold: true } }), cell(r, fw[1]), cell(["☐ Yes", "☐ No"], fw[2]), cell(" ", fw[3])] }))]));

kids.push(h1("Part E. Specific lines to confirm"));
const lw = [2300, 3638, 3700];
kids.push(table(lw, [headerRow(lw, ["Lines", "What the data shows", "Which is right? (tick one, or explain)"]),
  ...lines.map(([l, s, o]) => new TableRow({ cantSplit: true, children: [cell(l, lw[0], { run: { bold: true } }), cell(s, lw[1]),
    cell([p([run(`☐ ${o[0]}`)], { spacing: { after: 40 } }), p([run(`☐ ${o[1]}`)], { spacing: { after: 40 } }), p([run("☐ Other: ")], { spacing: { after: 0 } })], lw[2])] }))]));

kids.push(h1("Part F. Where the cord was actually made"));
kids.push(p("Some vendors are traders, so the vendor’s country is not the mill’s country. For each vendor, please give the country (and the mill, if known) where the cord was usually made. Write “unknown” if you don’t know."));
const vw = [3000, 2638, 2000, 2000];
kids.push(table(vw, [headerRow(vw, ["Vendor", "In the data", "Mill country", "Mill name (if known)"]),
  ...vendors.map(([v, d]) => new TableRow({ cantSplit: true, children: [cell(v, vw[0], { run: { bold: true } }), cell(d, vw[1]), cell(" ", vw[2]), cell(" ", vw[3])] }))]));

kids.push(h1("Part G. Documents to attach"));
kids.push(p("Please attach whichever of these you can. Tick each one you are sending."));
const dw = [900, W - 900];
kids.push(table(dw, docsToAttach.map((d) => new TableRow({ cantSplit: true, children: [cell("☐", dw[0]), cell(d, dw[1])] }))));
kids.push(space());
kids.push(h2("Anything else we should know about the PO data?"));
kids.push(table([W], [new TableRow({ cantSplit: true, children: [cell(blank(4), W)] })]));
kids.push(space());
kids.push(p([run("Thank you. Your answers are recorded as Phase 0 inputs and used exactly as written.", { italics: true, color: "5D6B70" })]));

const doc = new Document({
  creator: "Costing analyzer (Phase 0)", title: "NTC PO questionnaire",
  styles: {
    default: { document: { run: { font: FONT, size: 20 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 28, bold: true, color: ACC }, paragraph: { spacing: { before: 320, after: 140 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: FONT, size: 22, bold: true, color: "333333" }, paragraph: { spacing: { before: 200, after: 100 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [{ reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "NTC PO questionnaire · page ", font: FONT, size: 16, color: "888888" }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 16, color: "888888" })] })] }) },
    children: kids,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(process.argv[2], b); console.log("wrote", process.argv[2]); });
