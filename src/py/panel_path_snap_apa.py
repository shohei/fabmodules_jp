#
#-*- coding:utf-8 -*-
# panel_path_snap.py
#    MTM Snap virtual machine
#
# Neil Gershenfeld
# CBA MIT 11/28/11
# nmp update dec 3 2011: mm_per_step
#
# (c) Massachusetts Institute of Technology 2011
# Permission granted for experimental and personal use;
# license for commercial sale available from MIT.
#
# todo
#   APA out
#   APA send
#   process text entry
#   acceleration
#   job times
#
# imports
#
import wx,os
from math import *
import time
#
# machine definitions
#
mm_per_xstep = 0.00635 # stepper step size (400 steps/rev, 10 revs/in)
mm_per_ystep = 0.00635 # stepper step size ''
mm_per_zstep = 0.00635 # stepper step size ''
mm_per_jog_step = 0.00635 # jog step size
x_path = "" # APA path to x axis
y_path = "0" # APA path to y axis
z_path = "1" # APA path to z axis
spindle = "11" # APA path to spindle
#
# global variables
#
xstep = ystep = zstep = 0 # stepper position (step units)
spindle_state = 0 # on/off
move_state = 0 # on/off
#
# panel class
#
class path_snap_panel(wx.Panel):
   def __init__(self,parent):
      self.parent = parent
      self.parent.path_file = ''
      #
      # start/stop spindle
      #
      def spindle(event):
         global spindle_state
         spindle_state = 1 - spindle_state
         if (spindle_state == 1):
            spindle_button.SetLabel('スピンドル停止')
         else:
            spindle_button.SetLabel('on')
      #
      # start/stop job
      #
      def start(event,start_line=5):
         global move_state
         move_state = 1 - move_state
         if (move_state == 1):
            if (self.parent.path_file == ''):
               print "panel_path_snap: oops -- need path file"
               move_state = 0
               return
            start_button.SetLabel('停止')
            pause_button.SetLabel('一時停止')
            start = time.time()
            send_job(start_line)
            end = time.time()
            nsegment = float(segment.GetValue())
            print "%f sec, %f sec/segment"%((end-start),(end-start)/nsegment)
         else:
            start_button.SetLabel('開始')
      #
      # send job
      #
      def send_job(start_line):
         global move_state
         global nx,ny,nz,dx,dy,dz,x0,y0,z0
         #
         # read path
         #
         path_file = open(self.parent.path_file,'r')
         lines = path_file.readlines()
         segment_label.SetLabel("/"+str(len(lines)-1))
         dof = int(lines[0].split()[0])
         if (dof != 3):
            print "panel_path_snap: oops -- need a 3D path"
            return
         units = lines[1] # currently ignored, mm assumed
         nx = int(lines[2].split()[0])
         ny = int(lines[2].split()[1])
         nz = int(lines[2].split()[2])
         dx = float(lines[3].split()[0])
         dy = float(lines[3].split()[1])
         dz = float(lines[3].split()[2])
         x0 = float(lines[4].split()[0])
         y0 = float(lines[4].split()[1])
         z0 = float(lines[4].split()[2])
         path_file.close()
         #
         # get GUI values
         #
         speed_move = float(move_speed.GetValue())
         speed_jog = float(jog_speed.GetValue())
         height_jog = float(jog_height.GetValue())
         #
         # loop over path
         #
         for i in range(start_line,len(lines)):
            #
            # check for GUI events
            #
            wx.Yield()
            #
            # quit if stopped
            #
            if (move_state == 0):
               return
            #
            # read next line
            #
            line = lines[i].split()
            #
            # start of new segment?
            #
            if (line[0] == '.'):
               #
               # yes, clear old point and continue
               #
               (xold,yold,zold) = ([],[],[])
               continue
            #
            # no, go to next point
            #
            x = int(line[0])
            y = int(line[1])
            z = int(line[2])
            #
            # first point in segment?
            #
            if (xold == []):
               #
               # yes, jog there and move down
               #
               move_z_abs_mm(height_jog,speed_jog)
               move_xy_abs_path(x,y,speed_jog)
               move_z_abs_path(z,speed_move)
            else:
               #
               # no, move there
               #
               move_xyz_abs_path(x,y,z,speed_move)
            #
            # save old point
            #
            (xold,yold,zold) = (x,y,z)
            #
            # update segment counter and continue
            #
            segment.SetValue(str(i))
         #
         # finish
         #
         move_state = 0
         start_button.SetLabel('開始')
         segment_label.SetLabel("セグメント")
      #
      # pause
      #
      def pause(event):
         global move_state
         print "pause"
         if (move_state == 1):
            move_state = 0
            start_button.SetLabel("開始")
            pause_button.SetLabel("続行")
         elif (pause_button.GetLabel() == "続行"):
            start(0,int(segment.GetValue()))
      #
      # APA send z, stepper step units, ms time units
      #
      def apa_send_z(dz,time):
         command = "apa_send {^"+z_path+"|"+str(dz)+","+str(time)+"}"
         #print command
         os.system('echo "'+command+'" > /dev/null')
         # os.system(command)
      #
      # APA send xy, stepper step units, ms time units
      #
      def apa_send_xy(dx,dy,time):
         command = "apa_send {^"+x_path+"|"+str(dx)+","+str(time)+"}{^"+y_path+"|"+str(dy)+","+str(time)+"}"
         #print command
         os.system('echo "'+command+'" > /dev/null')
         # os.system(command)
      #
      # APA send xyz, stepper step units, ms time units
      #
      def apa_send_xyz(dx,dy,dz,time):
         command = "apa_send {^"+x_path+"|"+str(dx)+","+str(time)+"}{^"+y_path+"|"+str(dy)+","+str(time)+"}{^"+z_path+"|"+str(dz)+","+str(time)+"}"
         #print command
         os.system('echo "'+command+'" > /dev/null')
         # os.system(command)
      #
      # move xy absolute, path units
      #
      def move_xy_abs_path(xi,yi,speed):
         global xstep,ystep
         global mm_per_xstep,mm_per_ystep
         global nx,ny,nz,dx,dy,dz,x0,y0
         if (nx != 1):
            x = x0 + dx*xi/(nx-1.0)
         else:
            x = x0
         if (ny != 1):
            y = y0 + dy*yi/(ny-1.0)
         else:
            y = y0
         xpos.SetValue("%.3f"%x)
         ypos.SetValue("%.3f"%y)
         deltax = x - xstep*mm_per_xstep
         deltay = y - ystep*mm_per_ystep
         dxstep = int(deltax/mm_per_xstep)
         xstep += dxstep
         dystep = int(deltay/mm_per_ystep)
         ystep += dystep
         distance = sqrt(deltax*deltax+deltay*deltay)
         time = int(1000* distance / speed)
         apa_send_xy(dxstep,dystep,time)
      #
      # move xyz absolute, path units
      #
      def move_xyz_abs_path(xi,yi,zi,speed):
         global xstep,ystep,zstep
         global mm_per_xstep,mm_per_ystep,mm_per_zstep
         global nx,ny,nz,dx,dy,dz,x0,y0,z0
         if (nx != 1):
            x = x0 + dx*xi/(nx-1.0)
         else:
            x = x0
         if (ny != 1):
            y = y0 + dy*yi/(ny-1.0)
         else:
            y = y0
         if (nz != 1):
            z = z0 + dz*zi/(nz-1.0)
         else:
            z = z0
         xpos.SetValue("%.3f"%x)
         ypos.SetValue("%.3f"%y)
         zpos.SetValue("%.3f"%z)
         deltax = x - xstep*mm_per_xstep
         deltay = y - ystep*mm_per_ystep
         deltaz = z - zstep*mm_per_zstep
         dxstep = int(deltax/mm_per_xstep)
         xstep += dxstep
         dystep = int(deltay/mm_per_ystep)
         ystep += dystep
         dzstep = int(deltaz/mm_per_zstep)
         zstep += dzstep
         distance = sqrt(deltax*deltax+deltay*deltay+deltaz*deltaz)
         time = int(1000* distance / speed)
         apa_send_xyz(dxstep,dystep,dzstep,time)
      #
      # move z absolute, path units
      #
      def move_z_abs_path(z,speed):
         global zstep
         global mm_per_zstep
         global nz,dz,z0
         if (nz != 1):
            z = z0 + dz*zi/(nz-1.0)
         else:
            z = z0
         zpos.SetValue("%.3f"%z)
         deltaz = z - zstep*mm_per_zstep
         dzstep = int(deltaz/mm_per_zstep)
         zstep += dzstep
         distance = sqrt(deltaz*deltaz)
         time = int(1000* distance / speed)
         apa_send_z(dzstep,time)
      #
      # move z absolute, mm units
      #
      def move_z_abs_mm(z,speed):
         global zstep
         global mm_per_zstep
         zpos.SetValue("%.3f"%z)
         deltaz = z - zstep*mm_per_zstep
         dzstep = int(deltaz/mm_per_zstep)
         zstep += dzstep
         distance = sqrt(deltaz*deltaz)
         time = int(1000* distance / speed)
         apa_send_z(dzstep,time)
      #
      # move xyz relative, mm units
      #
      def move_xyz_rel_mm(dx,dy,dz,speed):
         global xstep,ystep,zstep
         global mm_per_xstep,mm_per_ystep,mm_per_zstep
         dxstep = int(dx / mm_per_xstep)
         xstep += dxstep
         xpos.SetValue("%.3f"%(xstep*mm_per_xstep))
         dystep = int(dy / mm_per_xstep)
         ystep += dystep
         ypos.SetValue("%.3f"%(ystep*mm_per_xstep))
         dzstep = int(dz / mm_per_xstep)
         zstep += dzstep
         zpos.SetValue("%.3f"%(zstep*mm_per_xstep))
         distance = sqrt(dx*dx+dy*dy+dz*dz)
         time = int(1000* distance / speed)
         apa_send_xyz(dxstep,dystep,dzstep,time)
      #
      # move left mouse down
      #
      def left_down(event):
         global move_state
         move_state = 1
         left_button.SetLabel('左移動')
         while 1:
            wx.Yield()
            if (move_state == 0):
               return
            move_xyz_rel_mm(-mm_per_jog_step,0,0,float(jog_speed.GetValue()))
      #
      # move left mouse up
      #
      def left_up(event):
         global move_state
         move_state = 0
         left_button.SetLabel('左移動')
      #
      # move right mouse down
      #
      def right_down(event):
         global move_state
         move_state = 1
         right_button.SetLabel('右移動')
         while 1:
            wx.Yield()
            if (move_state == 0):
               return
            move_xyz_rel_mm(mm_per_jog_step,0,0,float(jog_speed.GetValue()))
      #
      # move right mouse up
      #
      def right_up(event):
         global move_state
         move_state = 0
         right_button.SetLabel('右移動')
      #
      # move forward mouse down
      #
      def forward_down(event):
         global move_state
         move_state = 1
         forward_button.SetLabel('前進')
         while 1:
            wx.Yield()
            if (move_state == 0):
               return
            move_xyz_rel_mm(0,-mm_per_jog_step,0,float(jog_speed.GetValue()))
      #
      # move forward mouse up
      #
      def forward_up(event):
         global move_state
         move_state = 0
         forward_button.SetLabel('前進')
      #
      # move back mouse down
      #
      def back_down(event):
         global move_state
         move_state = 1
         back_button.SetLabel('後退')
         while 1:
            wx.Yield()
            if (move_state == 0):
               return
            move_xyz_rel_mm(0,mm_per_jog_step,0,float(jog_speed.GetValue()))
      #
      # move back mouse up
      #
      def back_up(event):
         global move_state
         move_state = 0
         back_button.SetLabel('後退')
      #
      # move up mouse down
      #
      def up_down(event):
         global move_state
         move_state = 1
         up_button.SetLabel('上昇')
         while 1:
            wx.Yield()
            if (move_state == 0):
               return
            move_xyz_rel_mm(0,0,mm_per_jog_step,float(jog_speed.GetValue()))
      #
      # move up mouse up
      #
      def up_up(event):
         global move_state
         move_state = 0
         up_button.SetLabel('上昇')
      #
      # move down mouse down
      #
      def down_down(event):
         global move_state
         move_state = 1
         down_button.SetLabel('下降')
         while 1:
            wx.Yield()
            if (move_state == 0):
               return
            move_xyz_rel_mm(0,0,-mm_per_jog_step,float(jog_speed.GetValue()))
      #
      # move down mouse up
      #
      def down_up(event):
         global move_state
         move_state = 0
         down_button.SetLabel('下降')
      #
      # zero x
      #
      def zero_x(event):
         global xstep
         xstep = 0
         xpos.SetValue("0.000")
      #
      # zero y
      #
      def zero_y(event):
         global ystep
         ystep = 0
         ypos.SetValue("0.000")
      #
      # zero z
      #
      def zero_z(event):
         global zstep
         zstep = 0
         zpos.SetValue("0.000")
      #
      # zero xyz
      #
      def zero_xyz(event):
         global xstep,ystep,zstep
         xstep = 0
         xpos.SetValue("0.000")
         ystep = 0
         ypos.SetValue("0.000")
         zstep = 0
         zpos.SetValue("0.000")
      #
      # home
      #
      def home(event):
         speed_jog = float(jog_speed.GetValue())
         height_jog = float(jog_height.GetValue())
         move_z_abs_mm(height_jog,speed_jog)
         move_xy_abs_path(0,0,speed_jog)
      #
      # panel
      #
      wx.Panel.__init__(self,parent)
      self.sizer = wx.GridBagSizer(10,10)
      self.SetSizer(self.sizer)
      #
      # label
      #
      label = wx.StaticText(self,label='MTM Snap型式に変換')
      bold_font = wx.Font(10,wx.DEFAULT,wx.NORMAL,wx.BOLD)
      label.SetFont(bold_font)
      self.sizer.Add(label,(0,0),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      # controls
      #
      mtm_panel = wx.Panel(self)
      mtm_sizer = wx.GridBagSizer(10,10)
      mtm_panel.SetSizer(mtm_sizer)
      #
      mtm_sizer.Add(wx.StaticText(mtm_panel,label='x y z (mm)'),(0,0),flag=wx.ALIGN_RIGHT)
      xpos = wx.TextCtrl(mtm_panel,-1,'0.000')
      mtm_sizer.Add(xpos,(0,1),flag=wx.ALIGN_CENTER_HORIZONTAL)
      ypos = wx.TextCtrl(mtm_panel,-1,'0.000')
      mtm_sizer.Add(ypos,(0,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      zpos = wx.TextCtrl(mtm_panel,-1,'0.000')
      mtm_sizer.Add(zpos,(0,3),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      zero_xyz_button = wx.Button(mtm_panel,label='xyzの原点設定')
      zero_xyz_button.Bind(wx.EVT_BUTTON,zero_xyz)
      mtm_sizer.Add(zero_xyz_button,(1,0),flag=wx.ALIGN_CENTER_HORIZONTAL)
      zero_x_button = wx.Button(mtm_panel,label='xの原点設定')
      zero_x_button.Bind(wx.EVT_BUTTON,zero_x)
      mtm_sizer.Add(zero_x_button,(1,1),flag=wx.ALIGN_CENTER_HORIZONTAL)
      zero_y_button = wx.Button(mtm_panel,label='yの原点設定')
      zero_y_button.Bind(wx.EVT_BUTTON,zero_y)
      mtm_sizer.Add(zero_y_button,(1,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      zero_z_button = wx.Button(mtm_panel,label='zの原点設定')
      zero_z_button.Bind(wx.EVT_BUTTON,zero_z)
      mtm_sizer.Add(zero_z_button,(1,3),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      home_button = wx.Button(mtm_panel,label='始点')
      home_button.Bind(wx.EVT_BUTTON,home)
      mtm_sizer.Add(home_button,(2,0),flag=wx.ALIGN_CENTER_HORIZONTAL)
      left_button = wx.Button(mtm_panel,label='左移動')
      left_button.Bind(wx.EVT_LEFT_DOWN,left_down)
      left_button.Bind(wx.EVT_LEFT_UP,left_up)
      mtm_sizer.Add(left_button,(3,0),flag=wx.ALIGN_CENTER_HORIZONTAL)
      back_button = wx.Button(mtm_panel,label='後退')
      back_button.Bind(wx.EVT_LEFT_DOWN,back_down)
      back_button.Bind(wx.EVT_LEFT_UP,back_up)
      mtm_sizer.Add(back_button,(2,1),flag=wx.ALIGN_CENTER_HORIZONTAL)
      mtm_sizer.Add(wx.StaticText(mtm_panel,label='ジョグ'),(3,1),flag=(wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER))
      forward_button = wx.Button(mtm_panel,label='前進')
      forward_button.Bind(wx.EVT_LEFT_DOWN,forward_down)
      forward_button.Bind(wx.EVT_LEFT_UP,forward_up)
      mtm_sizer.Add(forward_button,(4,1),flag=wx.ALIGN_CENTER_HORIZONTAL)
      right_button = wx.Button(mtm_panel,label='右移動')
      right_button.Bind(wx.EVT_LEFT_DOWN,right_down)
      right_button.Bind(wx.EVT_LEFT_UP,right_up)
      mtm_sizer.Add(right_button,(3,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      up_button = wx.Button(mtm_panel,label='上昇')
      up_button.Bind(wx.EVT_LEFT_DOWN,up_down)
      up_button.Bind(wx.EVT_LEFT_UP,up_up)
      mtm_sizer.Add(up_button,(2,3),flag=wx.ALIGN_CENTER_HORIZONTAL)
      down_button = wx.Button(mtm_panel,label='下降')
      down_button.Bind(wx.EVT_LEFT_DOWN,down_down)
      down_button.Bind(wx.EVT_LEFT_UP,down_up)
      mtm_sizer.Add(down_button,(3,3),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      mtm_sizer.Add(wx.StaticText(mtm_panel,label='スピード (mm/s)'),(4,0),flag=(wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_BOTTOM))
      move_speed = wx.TextCtrl(mtm_panel,-1,'1')
      mtm_sizer.Add(move_speed,(5,0),flag=wx.ALIGN_CENTER_HORIZONTAL)
      mtm_sizer.Add(wx.StaticText(mtm_panel,label='ジョグの速度 (mm/s) z (mm)'),(4,2),span=(1,2),flag=(wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_BOTTOM))
      jog_speed = wx.TextCtrl(mtm_panel,-1,'10')
      mtm_sizer.Add(jog_speed,(5,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      jog_height = wx.TextCtrl(mtm_panel,-1,'1')
      mtm_sizer.Add(jog_height,(5,3),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      mtm_sizer.Add(wx.StaticText(mtm_panel,label='スピンドル'),(6,0),flag=(wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL))
      spindle_button = wx.Button(mtm_panel,label='on')
      spindle_button.Bind(wx.EVT_BUTTON,spindle)
      mtm_sizer.Add(spindle_button,(6,1),flag=wx.ALIGN_CENTER_HORIZONTAL)
      mtm_sizer.Add(wx.StaticText(mtm_panel,label='スピード (rpm)'),(6,2),flag=(wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL))
      spindle_speed = wx.TextCtrl(mtm_panel,-1,'10000')
      mtm_sizer.Add(spindle_speed,(6,3),flag=wx.ALIGN_CENTER_HORIZONTAL)
      #
      start_button = wx.Button(mtm_panel,label='開始')
      start_button.Bind(wx.EVT_BUTTON,start)
      mtm_sizer.Add(start_button,(7,0),flag=wx.ALIGN_CENTER_HORIZONTAL)
      pause_button = wx.Button(mtm_panel,label='一時停止')
      pause_button.Bind(wx.EVT_BUTTON,pause)
      mtm_sizer.Add(pause_button,(7,1),flag=wx.ALIGN_CENTER_HORIZONTAL)
      segment = wx.TextCtrl(mtm_panel,-1,'0')
      mtm_sizer.Add(segment,(7,2),flag=wx.ALIGN_CENTER_HORIZONTAL)
      segment_label = wx.StaticText(mtm_panel,label='セグメント')
      mtm_sizer.Add(segment_label,(7,3),flag=(wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL))
      #
      self.sizer.Add(mtm_panel,(1,0),flag=(wx.ALIGN_CENTER_HORIZONTAL))
      #
      # fit
      #
      self.Fit()
