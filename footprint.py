from pydataobj import *
from tfsdata import *
import matplotlib.pyplot as pl
import matplotlib.delaunay
from convexhull import convex_hull
import numpy as _n
import os
from glob import glob
import re
import gzip

def find_res_xcross(m,n,q,xs,y1,y2,out):
#  print 'x=%d'% (xs),
  if n!=0:
    m,n,q,xs,y1,y2=map(float,(m,n,q,xs,y1,y2))
    ys=(q-m*xs)/n
#    print 'ys=%g'%ys,
#    print '%g<=ys<=%g'%(y1,y2),
    if ys>=y1 and ys<=y2:
#      print [xs,ys],
      out.append((xs,ys))
#  print

def find_res_ycross(m,n,q,ys,x1,x2,out):
#  print 'y=%d'% (ys),
  if m!=0:
    m,n,q,ys,y1,y2=map(float,(m,n,q,ys,x1,x2))
    xs=(q-n*ys)/m
#    print 'xs=%g'%xs,
#    print '%g<=xs<=%g'%(x1,x2),
    if xs>=x1 and xs<=x2:
#      print [xs,ys]
      out.append((xs,ys))
#  print

def get_res_box(m,n,a=0,b=1,c=0,d=1):
  """m,n,q resonance integers
     a,b,c,d box parameters
  """
  order=int(_n.ceil(abs(m)*max(abs(a),abs(b))+abs(n)*max(abs(c),abs(d))))
  out=[]
  for q in range(-order,+order+1):
    points=[]
#    print '%2d*x+%2d*y=%2d' % (m,n,q)
    find_res_xcross(m,n,q,a,c,d,points)
    find_res_xcross(m,n,q,b,c,d,points)
    find_res_ycross(m,n,q,c,a,b,points)
    find_res_ycross(m,n,q,d,a,b,points)
    points=list(set(points))
    if len(points)>1:
      out.append(points)
  return out

def getmn(o,s='b',diff=False):
  out=[]
  for m in range(0,o+1):
    n=o-m
    if 'b' in s and n%2==0:
      out.append( (m,n) )
      if diff:
        out.append( (m,-n) )
#      print m,n
#      print m,-n
    if 'a' in s and n%2==1:
      out.append( (m,n) )
      if diff:
        out.append( (m,-n) )
#      print m,n
#      print m,-n
  return out

def plot_res_box(m,n,a=0,b=1,c=0,d=1,color='k'):
  points=get_res_box(m,n,a,b,c,d)
  for c in points:
    x,y=zip(*c)
    pl.plot(x,y,'%s'%color)


def plot_res_order_box(o,a=0,b=1,c=0,d=1,c1='k',c2='r',diff=False):
  for m,n in getmn(o,'b',diff=diff):
    # print 'b%s: m=%d n=%d'%(o,m,n)
    plot_res_box(m,n,a=a,b=b,c=c,d=d,color=c1)
  for m,n in getmn(o,'a',diff=diff):
    # print 'a%s: m=%d n=%d'%(o,m,n)
    plot_res_box(m,n,a=a,b=b,c=c,d=d,color=c2)


def plot_res(m,n,color='k'):
  a,b=pl.xlim()
  c,d=pl.ylim()
  points=get_res_box(m,n,a,b,c,d)
  for c in points:
    x,y=zip(*c)
    pl.plot(x,y,'-%s'%color)

def plot_res_order(o,c1='k',c2='r',diff=False):
  a,b=pl.xlim()
  c,d=pl.ylim()
  for m,n in getmn(o,'b',diff=diff):
    # print 'b%s: m=%d n=%d'%(o,m,n)
    plot_res_box(m,n,a=a,b=b,c=c,d=d,color=c1)
  for m,n in getmn(o,'a',diff=diff):
    # print 'a%s: m=%d n=%d'%(o,m,n)
    plot_res_box(m,n,a=a,b=b,c=c,d=d,color=c2)

#plot_res_box(1,0)
#plot_res_box(3,0)
#plot_res_box(2,1)


#a=c=0.28;b=d=0.34;
#map(plot_res_order,range(1,15))




def mkranges(nsigmax=12,nangles=7):
  ranges=[]
  for i in range(nangles):
    ranges.append([0,i])
  for i in range(nangles):
    ranges.append(slice(1+i,nangles*nsigmax+1,nangles))
  for i in range(nsigmax):
    ranges.append(slice(1+nangles*i,1+nangles*(i+1)))
  return ranges

def plot_grid(t,nsigmax=12,nangles=7,lw=1):
  ranges=mkranges(nsigmax,nangles)
  for i in ranges:
    if hasattr(i,'step'):
      lw= i.step==nangles and i.start/2. or 1
    pl.plot(t.x[i],t.y[i],'-k',lw=lw)

def plot_footprint(t,nsigmax=6,nangles=7,wp=(0.28,0.31),spread=0.01):
  ranges=mkranges(nsigmax,nangles)
  lw=1
  out=[]
  lbl=True
  name=''
  color=colorrotate()
  for i in ranges:
    if lbl:
       p=pl.plot(t.tunx[i],t.tuny[i],'-%s'%color,lw=lw,label=name)
       lbl=False
    else:
       p=pl.plot(t.tunx[i],t.tuny[i],'-%s'%color,lw=lw)
    out.append(p[0])
  pl.ylabel('$Q_y$')
  pl.xlabel('$Q_x$')
  pl.grid(True)
  qx,qy=wp
  pl.xlim(qx-spread,qx+spread)
  pl.ylim(qy-spread,qy+spread)
  return out

mycolors=list('rgbcm')

def colorrotate():
  c=mycolors.pop(0);mycolors.append(c)
  return c


def mkplot(l,n,s):
  l,n,s=map(int,(l,n,s))
  fn='jobslhc3_%d_mb_%d_v2/dynaptune_%d.tfs'% (l,n,s)
  t=dataobj(tfsdata.open(fn))
  c=mycolors.pop(0);mycolors.append(c)
  plot_footprint(t,fn,nsigmax=12,color='c')
  return t

def triangulate(t):
  tr=matplotlib.delaunay.triangulate.Triangulation(t.tunx,t.tuny)
  for i in tr.triangle_nodes:
    plot(t.tunx[i],t.tuny[i])


#fn='/afs/cern.ch/project/uslarp/rdemaria/work/slhc3_1/dynamptune_thin_8282.tfs'
#t=dataobj(tfsdata.open(fn))
#c=mycolors.pop(0);mycolors.append(c)
##plot_grid(t,12)
#plot_footprint(t,fn,nsigmax=6,c='k')
#
#
#fn='/afs/cern.ch/project/uslarp/rdemaria/work/slhc3_2/dynamptune_thin_8282.tfs'
#t=dataobj(tfsdata.open(fn))
##plot_grid(t,12)
#plot_footprint(t,fn,nsigmax=6,c='k')
#
#
#fn='/afs/cern.ch/project/uslarp/rdemaria/work/slhc3_3/dynamptune_thin_8282.tfs'
#t=dataobj(tfsdata.open(fn))
#c=mycolors.pop(0);mycolors.append(c)
##plot_grid(t,12)
#plot_footprint(t,fn,nsigmax=6,c='k')
#
#mkplot(1,8282,1);mkplot(2,8282,1); mkplot(3,8282,1);


#for i in range(1,61):
#  try:
#    mkplot(3,8282,i)
#  except:
#    print 'error on',i
#
#xlim(0.298,0.312)
#ylim(0.3165,0.3205)

def change_alpha(ll,alpha):
  for a in ll:
    hasasttr(a,'set_alpha') and a.set_alpha(alpha) or change_alpha(a,alpha)

#regexp=re.compile('dynaptune_(..)(..)_(....)_dqx(......)_dqy(......)(.?)')
#def mkfn(bb,ir,squeeze,dqx,dqy,opt):
#  return 'dynaptune_%s%s_%s_dqx%+6.3f_dqy%+6.3f%s'%(bb,ir,squeeze,dqx,dqy,opt)
#
#def load(bb,ir,squeeze,dqx,dqy,opt):
#  t=dataobj(tfsdata.open(mkfn(bb,ir,squeeze,dqx,dqy,opt)))
#  t.tunx-=dqx; t.tuny-=dqy
#  return t
#
#data={}
#for i in glob('dynaptune*'):
#  bb,ir,squeeze,dqx,dqy,opt=regexp.match(i).groups()
#  dqx=float(dqx)
#  dqy=float(dqy)
#  print bb,ir,squeeze,dqx,dqy,opt
#  t=load(bb,ir,squeeze,dqx,dqy,opt)
#  data[(bb,ir,squeeze,opt)]=t



