import cdo as cdo; cdo = cdo.Cdo() # recommended import
import os
from numpy import squeeze
from netCDF4 import Dataset,num2date,date2num

os.system( 'rm -rf /tmp/cdo*') # clean out tmp to make space for CDO processing.

def loadvar( ifile , varname, remap='', start_date='', end_date='', timmean=False, zonmean=False):
        """  
            Load a CMIP5 netcdf variable "varname" from "ifile" and optionally 1) distance
            weighted remap to a given grid (e.g. 'r360x180), 2) select a date range between 
            start_date and end_date (format: 'YYYY-MM-DD'), 3) time-mean over the whole 
            record, or between the selected dates and 4) zonal mean. Requires netCDF4, CDO 
            and CDO python bindings. Returns a masked array, var.
            
            If zonmean=True and remap=True, the zonal mean is done first, so the remap
            will in that case only specify the latitude-grid, with 1-point in x, e.g.: 
            remap=r180x1.
          """
          
        # Open the variable using NetCDF4 to get scale and offset attributes.  
        nc = Dataset( ifile , 'r' )
        ncvar = nc.variables[ varname ]
        
        date_range = start_date + ',' + end_date

        # parse through all options, and load the data using CDO.
        if ( timmean == True ) and ( start_date ) and ( remap ) and (zonmean == True) :
            in_str = "-zonmean -timmean -seldate," + date_range + "  -selvar," + varname + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )

        elif ( timmean == True ) and ( start_date ) and ( remap ) :
            in_str = "-timmean -seldate," + date_range + " " + ifile
            var = cdo.remapdis( remap, input = in_str, returnMaArray=varname )
  
        elif ( timmean == True ) and ( start_date ) and ( zonmean ) :
            in_str = "-timmean -seldate," + date_range + " -selvar," + varname + " " + ifile
            var = cdo.zonmean( input = in_str, returnMaArray=varname )           
    
        elif ( timmean == True ) and ( zonmean ) and ( remap ) :
            in_str = "-zonmean -timmean -selvar," + varname + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )     
  
        elif ( zonmean ) and ( start_date ) and ( remap ) :
            in_str = "-zonmean -seldate," + date_range + " -selvar," + varname + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )   
  
        elif ( timmean == True ) and ( remap ) :
            in_str = "-timmean" + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )

        elif ( start_date ) and ( remap ) :
            in_str = "-seldate," + date_range + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )

        elif  ( timmean == True ) and ( start_date ):
            var = cdo.timmean( input = cdo.seldate( date_range, input=ifile ), 
                               returnMaArray=varname )
                               
        elif  ( timmean == True ) and ( zonmean == True ):
	    in_str = "-timmean -selvar," + varname + " " + ifile
            var = cdo.zonmean( input=in_str, returnMaArray=varname )       
            
        elif  ( start_date ) and ( zonmean == True ):
	    in_str = "-seldate," + date_range +  " -selvar," + varname + " " + ifile
            var = cdo.zonmean( input=in_str, returnMaArray=varname )    
            
        elif  ( remap ) and  ( zonmean == True ):
            in_str = "-zonmean -selvar," + varname + " " + ifile
            var = cdo.remapdis( remap , input = in_str, returnMaArray=varname )            
            
        elif ( remap ) :
            var = cdo.remapdis( remap , input = ifile, returnMaArray=varname )

        elif ( timmean == True ):
            var = cdo.timmean( input=ifile, returnMaArray=varname ) 

        elif ( start_date ):
            var = cdo.seldate( date_range, input=ifile, returnMaArray=varname )

        elif ( zonmean == True ):
            in_str =  "-selvar," + varname + " " + ifile
            var = cdo.zonmean( input=in_str, returnMaArray=varname )

        else :
            #var = cdo.zonmean( input=in_str, returnMaArray=varname )
            var = cdo.setrtomiss(1e34,1.1e34, input=ifile, returnMaArray=varname)  
            #var = ncvar[:]      
            
        # Apply any scaling and offsetting needed:
        try:
	    var_offset = ncvar.add_offset
        except:
	    var_offset = 0
        try:
	    var_scale = ncvar.scale_factor
        except:
	    var_scale = 1	
            
        var = var*var_scale + var_offset    
        #return var
        return squeeze( var )
         
def get_dimensions(ifile, varname, toDatetime=False):
        """Returns the dimensions of variable varname in file ifile as a dictionary.
        If one of the dimensions begins with lat (Lat, Latitude and Latitudes), it 
        will be returned with a key of lat, and similarly for lon. If to a Datetime=True, 
        the time dimension is converted to a datetime. 
        """
        
        # Open the variable using NetCDF4 
        nc = Dataset( ifile , 'r' )
        ncvar = nc.variables[ varname ]
             
        dimensions={}
        for dimension in ncvar.dimensions:
	        if dimension.lower().startswith('lat'):
		    dimensions['lat'] = nc.variables[ dimension ][:]
		elif dimension.lower().startswith('lon'):
		    dimensions['lon'] = nc.variables[ dimension ][:]
	        elif dimension.lower().startswith('time'):
		    dimensions['time'] = nc.variables[ dimension ][:]    
		elif toDatetime==True and (dimension.lower().startswith('time') ):
	            # Following Phil Austin's slice_nc
                    nc_time = data_nc.variables['time']
                    dimensions['time'] = num2date(time_nc[:], nc_time.units, nc_time.calendar)
	        else:  
	            dimensions[dimension] = nc.variables[ dimension ][:]
	    
	return dimensions
