import React from "react";

// Official-style luxury vector brand marks for bespoke sartorial houses
export const BRAND_LOGOS = [
  {
    id: "loro-piana",
    name: "Loro Piana",
    origin: "Quarona · Italy",
    type: "Superfine Wool & Cashmere",
    svg: (
      <svg viewBox="0 0 180 50" className="h-8 w-auto fill-current">
        {/* Loro Piana Crest */}
        <g transform="translate(10, 8) scale(0.7)">
          <path d="M16 2 L22 10 L28 2 L32 12 L12 12 Z" opacity="0.9" />
          <path d="M14 14 Q22 16 30 14 L28 26 Q22 30 16 26 Z" stroke="currentColor" strokeWidth="1.5" fill="none" />
          <circle cx="22" cy="20" r="3" />
        </g>
        {/* Loro Piana Typography */}
        <text x="44" y="26" fontFamily="'Playfair Display', 'Cormorant Garamond', Georgia, serif" fontSize="17" fontWeight="600" letterSpacing="0.06em">
          Loro Piana
        </text>
        <text x="45" y="38" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6.5" fontWeight="600" letterSpacing="0.28em" opacity="0.75">
          ITALY · 1924
        </text>
      </svg>
    ),
  },
  {
    id: "zegna",
    name: "ZEGNA",
    origin: "Trivero · Italy",
    type: "Trofeo & Oasi Cashmere",
    svg: (
      <svg viewBox="0 0 160 50" className="h-8 w-auto fill-current">
        {/* Zegna Horizon double stripe icon */}
        <rect x="8" y="14" width="22" height="3" rx="1.5" />
        <rect x="8" y="20" width="22" height="3" rx="1.5" opacity="0.75" />
        {/* Zegna typography */}
        <text x="38" y="27" fontFamily="'Montserrat', 'Arial Black', sans-serif" fontSize="19" fontWeight="800" letterSpacing="0.14em">
          ZEGNA
        </text>
        <text x="39" y="38" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6.5" fontWeight="600" letterSpacing="0.25em" opacity="0.75">
          TRIVERO 1910
        </text>
      </svg>
    ),
  },
  {
    id: "scabal",
    name: "SCABAL",
    origin: "Savile Row · London",
    type: "Super 180s Bespoke",
    svg: (
      <svg viewBox="0 0 170 50" className="h-8 w-auto fill-current">
        {/* Royal Crown Crest */}
        <g transform="translate(10, 10) scale(0.65)">
          <path d="M4 18 L8 6 L16 13 L24 6 L28 18 Z" stroke="currentColor" strokeWidth="1.5" fill="none" />
          <circle cx="8" cy="5" r="1.5" />
          <circle cx="16" cy="11" r="1.5" />
          <circle cx="24" cy="5" r="1.5" />
          <rect x="4" y="19" width="24" height="2.5" rx="1" />
        </g>
        {/* Scabal cursive / serif mark */}
        <text x="40" y="26" fontFamily="'Playfair Display', Georgia, serif" fontSize="18" fontWeight="700" letterSpacing="0.12em">
          SCABAL
        </text>
        <text x="41" y="38" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6.5" fontWeight="600" letterSpacing="0.22em" opacity="0.75">
          SAVILE ROW · LONDON
        </text>
      </svg>
    ),
  },
  {
    id: "vbc",
    name: "CANONICO",
    origin: "Biella 1663 · Italy",
    type: "Fine Tailoring Wool",
    svg: (
      <svg viewBox="0 0 200 50" className="h-8 w-auto fill-current">
        {/* Double Eagle / 1663 Crest */}
        <g transform="translate(8, 8) scale(0.7)">
          <path d="M14 6 C8 12 8 22 14 26 C20 22 20 12 14 6 Z" stroke="currentColor" strokeWidth="1.2" fill="none" />
          <circle cx="14" cy="16" r="3" />
        </g>
        <text x="36" y="22" fontFamily="'Playfair Display', Georgia, serif" fontSize="13" fontWeight="700" letterSpacing="0.1em">
          VITALE BARBERIS
        </text>
        <text x="36" y="34" fontFamily="'Playfair Display', Georgia, serif" fontSize="11" fontWeight="700" letterSpacing="0.18em">
          CANONICO 1663
        </text>
        <text x="37" y="43" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6" fontWeight="600" letterSpacing="0.24em" opacity="0.75">
          BIELLA · ITALY
        </text>
      </svg>
    ),
  },
  {
    id: "dormeuil",
    name: "DORMEUIL",
    origin: "Paris & London",
    type: "Amadeus & Silk",
    svg: (
      <svg viewBox="0 0 170 50" className="h-8 w-auto fill-current">
        {/* Shield with Ram / Golden Fleece */}
        <g transform="translate(10, 10) scale(0.65)">
          <path d="M6 4 H24 V18 Q24 28 15 32 Q6 28 6 18 Z" stroke="currentColor" strokeWidth="1.5" fill="none" />
          <path d="M10 14 Q15 10 20 14 Q15 20 10 14 Z" fill="currentColor" opacity="0.8" />
        </g>
        <text x="40" y="26" fontFamily="'Playfair Display', Georgia, serif" fontSize="17" fontWeight="700" letterSpacing="0.15em">
          DORMEUIL
        </text>
        <text x="41" y="38" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6.5" fontWeight="600" letterSpacing="0.22em" opacity="0.75">
          PARIS · LONDON 1842
        </text>
      </svg>
    ),
  },
  {
    id: "cerruti",
    name: "CERRUTI 1881",
    origin: "Biella · Italy",
    type: "Prestige Natural Fibres",
    svg: (
      <svg viewBox="0 0 175 50" className="h-8 w-auto fill-current">
        <text x="12" y="27" fontFamily="'Montserrat', 'DM Sans', sans-serif" fontSize="18" fontWeight="800" letterSpacing="0.18em">
          CERRUTI
        </text>
        <text x="135" y="27" fontFamily="'Playfair Display', Georgia, serif" fontSize="16" fontWeight="700" letterSpacing="0.08em" opacity="0.9">
          1881
        </text>
        <text x="13" y="39" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6.5" fontWeight="600" letterSpacing="0.28em" opacity="0.75">
          LANIFICIO F.LLI CERRUTI · BIELLA
        </text>
      </svg>
    ),
  },
  {
    id: "holland-sherry",
    name: "HOLLAND & SHERRY",
    origin: "Savile Row · Edinburgh",
    type: "Apparel Cloth Masters",
    svg: (
      <svg viewBox="0 0 190 50" className="h-8 w-auto fill-current">
        {/* Scottish Stag Horns */}
        <g transform="translate(8, 10) scale(0.65)">
          <path d="M6 8 Q14 2 14 16 M22 8 Q14 2 14 16" stroke="currentColor" strokeWidth="1.5" fill="none" />
          <circle cx="14" cy="18" r="2.5" />
        </g>
        <text x="36" y="24" fontFamily="'Playfair Display', Georgia, serif" fontSize="13" fontWeight="700" letterSpacing="0.12em">
          HOLLAND & SHERRY
        </text>
        <text x="37" y="37" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6.5" fontWeight="600" letterSpacing="0.22em" opacity="0.75">
          SAVILE ROW · LONDON 1836
        </text>
      </svg>
    ),
  },
  {
    id: "withmore",
    name: "WITHMORE",
    origin: "Tashkent Atelier",
    type: "Bespoke Sartorial Menswear",
    svg: (
      <svg viewBox="0 0 180 50" className="h-8 w-auto fill-current">
        {/* Withmore Monogram Crest */}
        <g transform="translate(10, 8) scale(0.7)">
          <circle cx="16" cy="18" r="14" stroke="currentColor" strokeWidth="1.5" fill="none" />
          <text x="9" y="23" fontFamily="'Playfair Display', serif" fontSize="15" fontWeight="700">
            W
          </text>
        </g>
        <text x="42" y="26" fontFamily="'Cormorant Garamond', 'Playfair Display', serif" fontSize="19" fontWeight="700" letterSpacing="0.22em">
          WITHMORE
        </text>
        <text x="43" y="38" fontFamily="system-ui, -apple-system, sans-serif" fontSize="6.5" fontWeight="700" letterSpacing="0.25em" opacity="0.8">
          BESPOKE ATELIER
        </text>
      </svg>
    ),
  },
];

