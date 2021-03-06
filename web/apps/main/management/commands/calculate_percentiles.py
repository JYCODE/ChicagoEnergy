from django.core.management.base import BaseCommand, CommandError
from main.models import CensusBlocks, Neighborhoods, MonthlyEnergy, Pledge
from django.db.models import Sum

import sys

class Command(BaseCommand):

    def handle(self, *args, **options):
        neighborhoods = Neighborhoods.objects.all()
        for neighborhood in neighborhoods:

            # BUILDING_SUBTYPE = ["All", "Single Family", "Multi < 7", "Multi 7+"]
            BUILDING_SUBTYPE = ["All"]
            # Aggregate the values to find the efficiency of the residential

            for sub_type in BUILDING_SUBTYPE:
                print >> sys.stderr, "Analyzing %s subtype of %s" %(sub_type, neighborhood.name)
                census_blocks = CensusBlocks.objects.filter(building_type = 'Residential',
                                                            building_subtype = sub_type,
                                                            neighborhood = neighborhood)
                kwh_list = []
                therm_list = []

                # third item in list is the percentile to be calculated later
                for census_block in census_blocks:
                    kwh_list.append([census_block.census_id, census_block.kwh_efficiency,0])
                    therm_list.append([census_block.census_id, census_block.therm_efficiency,0])

                sorted_kwh_list = sorted(kwh_list, key = lambda efficiency:efficiency[1])
                sorted_therm_list = sorted(therm_list, key = lambda efficiency:efficiency[1])

                for i, item in enumerate(sorted_kwh_list):
                    sorted_kwh_list[i][2] = float(i)/len(sorted_kwh_list)
                    sorted_therm_list[i][2] = float(i)/len(sorted_therm_list)

                for i,kwh in enumerate(sorted_kwh_list):
                    census_block_id = kwh[0]
                    census_block = CensusBlocks.objects.filter(census_id=census_block_id, 
                                                               building_type='Residential',
                                                               building_subtype=sub_type).update(kwh_percentile = kwh[2],
                                                                                                 kwh_rank = i+1)
                    # census_block.kwh_percentile = kwh[2]
                    # census_block.save()
                    if i%10 == 0:
                        print >> sys.stderr, "Evaluating kwh percentile %i of %i" %(i, len(sorted_kwh_list))

                for i,therm in enumerate(sorted_therm_list):
                    census_block_id = therm[0]
                    census_block = CensusBlocks.objects.filter(census_id=census_block_id, 
                                                               building_type='Residential',
                                                               building_subtype=sub_type).update(therm_percentile=therm[2],
                                                                                                 therm_rank = i+1)
                    # census_block.therm_percentile = therm[2]
                    # census_block.save()
                    if i%10 == 0:
                        print >> sys.stderr, "Evaluating therm percentile %i of %i" %(i, len(sorted_therm_list))