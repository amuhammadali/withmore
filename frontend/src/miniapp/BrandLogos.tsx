import React from "react";

// Authentic luxury vector brand logos for world-class fabric mills & bespoke houses
export const BRAND_LOGOS = [
  {
    id: "loro-piana",
    name: "Loro Piana",
    origin: "Italy · 1924",
    type: "Cashmere & Superfine Wool",
    svg: (
      <svg
        viewBox="0 0 170 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Loro Piana Authentic Heraldic Crest */}
        <g transform="translate(6, 4) scale(0.68)">
          <path
            d="M 18 2 L 23 9 L 28 2 L 32 10 L 14 10 Z"
            fill="currentColor"
            opacity="0.9"
          />
          <path
            d="M 12 12 Q 23 14 34 12 L 31 28 Q 23 33 15 28 Z"
            stroke="currentColor"
            strokeWidth="1.6"
            fill="none"
          />
          <circle cx="23" cy="21" r="3" fill="currentColor" />
          <path d="M 17 17 L 29 25 M 29 17 L 17 25" stroke="currentColor" strokeWidth="1" opacity="0.6" />
        </g>
        {/* Loro Piana Classic Serif Typography */}
        <text
          x="42"
          y="23"
          fontFamily="'Playfair Display', 'Cormorant Garamond', Georgia, serif"
          fontSize="18"
          fontWeight="600"
          letterSpacing="0.04em"
          fill="currentColor"
        >
          Loro Piana
        </text>
        <text
          x="43"
          y="35"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="7"
          fontWeight="700"
          letterSpacing="0.28em"
          opacity="0.7"
          fill="currentColor"
        >
          ITALY · 1924
        </text>
      </svg>
    ),
  },
  {
    id: "zegna",
    name: "ZEGNA",
    origin: "Trivero · 1910",
    type: "Trofeo & Oasi Cashmere",
    svg: (
      <svg
        viewBox="0 0 150 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Zegna Signifier Double Stripes */}
        <rect x="6" y="11" width="20" height="3" rx="1.5" fill="#c5a676" />
        <rect x="6" y="17" width="20" height="3" rx="1.5" fill="currentColor" opacity="0.75" />
        {/* ZEGNA Bold Modern Typography */}
        <text
          x="34"
          y="24"
          fontFamily="'Montserrat', 'Arial Black', system-ui, sans-serif"
          fontSize="19"
          fontWeight="800"
          letterSpacing="0.14em"
          fill="currentColor"
        >
          ZEGNA
        </text>
        <text
          x="35"
          y="35"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="6.5"
          fontWeight="700"
          letterSpacing="0.26em"
          opacity="0.7"
          fill="currentColor"
        >
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
      <svg
        viewBox="0 0 160 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Royal Savile Row Crown */}
        <g transform="translate(6, 6) scale(0.65)">
          <path
            d="M 3 18 L 7 5 L 15 12 L 23 5 L 27 18 Z"
            stroke="currentColor"
            strokeWidth="1.6"
            fill="none"
          />
          <circle cx="7" cy="4" r="1.8" fill="#c5a676" />
          <circle cx="15" cy="11" r="1.8" fill="#c5a676" />
          <circle cx="23" cy="4" r="1.8" fill="#c5a676" />
          <rect x="3" y="19" width="24" height="2.5" rx="1" fill="currentColor" />
        </g>
        {/* SCABAL Letterspaced Serif */}
        <text
          x="36"
          y="23"
          fontFamily="'Playfair Display', Georgia, serif"
          fontSize="18"
          fontWeight="700"
          letterSpacing="0.12em"
          fill="currentColor"
        >
          SCABAL
        </text>
        <text
          x="37"
          y="35"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="6.5"
          fontWeight="700"
          letterSpacing="0.22em"
          opacity="0.7"
          fill="currentColor"
        >
          SAVILE ROW · LONDON
        </text>
      </svg>
    ),
  },
  {
    id: "vbc",
    name: "CANONICO",
    origin: "Biella · 1663",
    type: "Fine Tailoring Wool",
    svg: (
      <svg
        viewBox="0 0 185 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* 1663 Italian Wool Seal */}
        <g transform="translate(6, 6) scale(0.65)">
          <path
            d="M 14 4 C 6 11 6 22 14 28 C 22 22 22 11 14 4 Z"
            stroke="currentColor"
            strokeWidth="1.4"
            fill="none"
          />
          <circle cx="14" cy="16" r="3" fill="#c5a676" />
        </g>
        <text
          x="32"
          y="18"
          fontFamily="'Playfair Display', Georgia, serif"
          fontSize="12"
          fontWeight="700"
          letterSpacing="0.1em"
          fill="currentColor"
        >
          VITALE BARBERIS
        </text>
        <text
          x="32"
          y="29"
          fontFamily="'Playfair Display', Georgia, serif"
          fontSize="10"
          fontWeight="700"
          letterSpacing="0.18em"
          fill="#c5a676"
        >
          CANONICO 1663
        </text>
        <text
          x="33"
          y="38"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="6"
          fontWeight="700"
          letterSpacing="0.25em"
          opacity="0.65"
          fill="currentColor"
        >
          BIELLA · ITALY
        </text>
      </svg>
    ),
  },
  {
    id: "dormeuil",
    name: "DORMEUIL",
    origin: "Paris & London",
    type: "Amadeus & Luxury Silk",
    svg: (
      <svg
        viewBox="0 0 165 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Golden Ram / Fleece Shield */}
        <g transform="translate(6, 6) scale(0.65)">
          <path
            d="M 5 4 H 23 V 17 Q 23 27 14 31 Q 5 27 5 17 Z"
            stroke="currentColor"
            strokeWidth="1.5"
            fill="none"
          />
          <path
            d="M 9 14 Q 14 10 19 14 Q 14 20 9 14 Z"
            fill="#c5a676"
          />
        </g>
        <text
          x="34"
          y="23"
          fontFamily="'Playfair Display', Georgia, serif"
          fontSize="17"
          fontWeight="700"
          letterSpacing="0.16em"
          fill="currentColor"
        >
          DORMEUIL
        </text>
        <text
          x="35"
          y="35"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="6.5"
          fontWeight="700"
          letterSpacing="0.22em"
          opacity="0.7"
          fill="currentColor"
        >
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
      <svg
        viewBox="0 0 165 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        <text
          x="6"
          y="23"
          fontFamily="'Montserrat', 'DM Sans', sans-serif"
          fontSize="17"
          fontWeight="800"
          letterSpacing="0.16em"
          fill="currentColor"
        >
          CERRUTI
        </text>
        <text
          x="115"
          y="23"
          fontFamily="'Playfair Display', Georgia, serif"
          fontSize="15"
          fontWeight="700"
          letterSpacing="0.08em"
          fill="#c5a676"
        >
          1881
        </text>
        <text
          x="7"
          y="35"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="6.5"
          fontWeight="700"
          letterSpacing="0.24em"
          opacity="0.7"
          fill="currentColor"
        >
          LANIFICIO F.LLI CERRUTI
        </text>
      </svg>
    ),
  },
  {
    id: "holland-sherry",
    name: "HOLLAND & SHERRY",
    origin: "Savile Row · 1836",
    type: "Apparel Cloth Masters",
    svg: (
      <svg
        viewBox="0 0 180 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Scottish Stag Horns Emblem */}
        <g transform="translate(6, 6) scale(0.65)">
          <path
            d="M 5 7 Q 13 1 13 15 M 21 7 Q 13 1 13 15"
            stroke="currentColor"
            strokeWidth="1.6"
            fill="none"
          />
          <circle cx="13" cy="18" r="2.5" fill="#c5a676" />
        </g>
        <text
          x="30"
          y="21"
          fontFamily="'Playfair Display', Georgia, serif"
          fontSize="13"
          fontWeight="700"
          letterSpacing="0.1em"
          fill="currentColor"
        >
          HOLLAND & SHERRY
        </text>
        <text
          x="31"
          y="34"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="6.5"
          fontWeight="700"
          letterSpacing="0.22em"
          opacity="0.7"
          fill="currentColor"
        >
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
      <svg
        viewBox="0 0 170 42"
        className="h-7 sm:h-8 w-auto fill-current"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Withmore Royal Monogram */}
        <g transform="translate(6, 5) scale(0.68)">
          <circle cx="16" cy="17" r="14" stroke="#c5a676" strokeWidth="1.6" fill="none" />
          <text
            x="8.5"
            y="22.5"
            fontFamily="'Playfair Display', Georgia, serif"
            fontSize="16"
            fontWeight="700"
            fill="currentColor"
          >
            W
          </text>
        </g>
        <text
          x="36"
          y="23"
          fontFamily="'Playfair Display', Georgia, serif"
          fontSize="18"
          fontWeight="700"
          letterSpacing="0.22em"
          fill="currentColor"
        >
          WITHMORE
        </text>
        <text
          x="37"
          y="35"
          fontFamily="system-ui, -apple-system, sans-serif"
          fontSize="6.5"
          fontWeight="700"
          letterSpacing="0.26em"
          fill="#c5a676"
        >
          BESPOKE ATELIER
        </text>
      </svg>
    ),
  },
];
