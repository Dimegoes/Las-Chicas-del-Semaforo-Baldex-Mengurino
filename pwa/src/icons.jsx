// Iconos de trazo simple (24x24) para no depender de librerias externas.
const PATHS = {
  back: <path d="M15 5l-7 7 7 7" />,
  dish: <><circle cx="12" cy="12" r="8.5" /><circle cx="9.5" cy="10" r="1.2" /><circle cx="14" cy="9" r="1" /><circle cx="14.5" cy="14" r="1.4" /><circle cx="10" cy="15" r="1" /></>,
  camera: <><path d="M4 8h3l2-3h6l2 3h3v11H4z" /><circle cx="12" cy="13" r="3.5" /></>,
  image: <><rect x="4" y="5" width="16" height="14" rx="2" /><circle cx="9" cy="10" r="1.5" /><path d="M5 17l5-5 4 4 2-2 3 3" /></>,
  chevron: <path d="M9 5l7 7-7 7" />,
  check: <path d="M5 12l5 5 9-10" />,
  undo: <><path d="M9 7L5 11l4 4" /><path d="M5 11h9a5 5 0 0 1 0 10h-3" /></>,
  calc: <><rect x="5" y="3" width="14" height="18" rx="2" /><path d="M8 7h8" /><path d="M8 12h.01M12 12h.01M16 12h.01M8 16h.01M12 16h.01M16 16h.01" /></>,
  list: <><path d="M9 6h11M9 12h11M9 18h11" /><path d="M4.5 6h.01M4.5 12h.01M4.5 18h.01" /></>,
  download: <><path d="M12 4v11" /><path d="M7 10l5 5 5-5" /><path d="M5 20h14" /></>,
}

export function Icon({ name, size = 22 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {PATHS[name]}
    </svg>
  )
}
