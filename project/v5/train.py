"""Shared metric and provenance utilities for v5."""
import hashlib
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def aggregate(results):
    ms=[r['metrics'][2] for r in results];nt=sum(m['target_notes'] for m in ms);na=sum(m['actual_notes'] for m in ms);tp=sum(m['matched'] for m in ms)
    p=tp/na if na else 0;r=tp/nt if nt else 0
    return dict(precision=p,recall=r,f1=2*p*r/(p+r) if p+r else 0,matched=tp,target_notes=nt,actual_notes=na,solver_warnings=sum(r['solver_warnings'] for r in results))
