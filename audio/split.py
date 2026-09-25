import subprocess, re, sys
groups = {
 'acertos': ['g01','g02','g03','g04','g05'],
 'capitulo1': ['c1-%02d'%i for i in range(1,24)],
 'capitulo2': ['c2-%02d'%i for i in range(1,18)],
}
for src, ids in groups.items():
    f = f'originais/{src}.mp3'
    out = subprocess.run(['ffmpeg','-hide_banner','-i',f,'-af','silencedetect=noise=-40dB:d=1.5','-f','null','-'],capture_output=True,text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', out)]
    ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', out)]
    dur = float(subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f],capture_output=True,text=True).stdout)
    assert len(ends) == len(ids)-1, (src, len(ends))
    segs = []; t0 = 0.0
    for s, e in zip(starts, ends):
        segs.append((max(0, t0), s + 0.15)); t0 = e - 0.1
    segs.append((t0, dur))
    for cid, (a, b) in zip(ids, segs):
        subprocess.run(['ffmpeg','-y','-loglevel','error','-ss',f'{a:.3f}','-to',f'{b:.3f}','-i',f,
          '-ac','1','-ar','24000','-b:a','48k',f'{cid}.mp3'], check=True)
        print(cid, round(b-a,2))
