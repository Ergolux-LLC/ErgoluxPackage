// Declarations to allow dynamic imports of GridStack's bundled files
// Adjust or expand types as you adopt a single import path.

declare module 'gridstack/dist/gridstack-all.js' {
  const value: any;
  export default value;
}

declare module 'gridstack/dist/gridstack.esm.js' {
  const value: any;
  export default value;
}

// Also allow the plain package import if types are missing
declare module 'gridstack' {
  const GridStack: any;
  export type GridStack = any;
  export default GridStack;
}
