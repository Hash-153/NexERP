import React, { useState } from 'react';

export function EDIX12TransactionInspector() {
  const [selectedTx, setSelectedTx] = useState('850');

  const raw850 = `ISA*00*          *00*          *ZZ*NEXERP         *ZZ*PARTNER        *260301*1200*U*00401*000000001*0*P*>~
GS*PO*NEXERP*PARTNER*20260301*1200*1*X*004010~
ST*850*0001~
BEG*00*SA*PO-2026-9901**20260301~
N1*VN*VANGUARD METALS*92*VN9821~
PO1*1*100*EA*245.00**VN*SKU-TITANIUM-ROTOR~
PID*F****PRECISION CNC TITANIUM ROTOR 48MM~
PO1*2*500*EA*12.50**VN*SKU-FASTENER-HEX-M8~
CTT*2~
SE*9*0001~
GE*1*1~
IEA*1*000000001~`;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">EDI X12 Electronic Data Interchange Inspector</h3>
          <p className="text-xs text-slate-500">ANSI ASC X12 syntax validator and segment element parser</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setSelectedTx('850')}
            className={`px-3 py-1 text-xs font-bold rounded ${selectedTx === '850' ? 'bg-blue-600 text-white' : 'bg-slate-100 dark:bg-slate-800'}`}
          >
            EDI 850 (PO)
          </button>
          <button
            onClick={() => setSelectedTx('856')}
            className={`px-3 py-1 text-xs font-bold rounded ${selectedTx === '856' ? 'bg-blue-600 text-white' : 'bg-slate-100 dark:bg-slate-800'}`}
          >
            EDI 856 (ASN)
          </button>
          <button
            onClick={() => setSelectedTx('810')}
            className={`px-3 py-1 text-xs font-bold rounded ${selectedTx === '810' ? 'bg-blue-600 text-white' : 'bg-slate-100 dark:bg-slate-800'}`}
          >
            EDI 810 (Invoice)
          </button>
        </div>
      </div>

      <pre className="p-4 bg-slate-950 text-emerald-400 font-mono text-xs rounded-lg overflow-x-auto leading-relaxed border border-slate-800">
        {raw850}
      </pre>
    </div>
  );
}
