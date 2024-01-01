# from absl import flags
import argparse
import collections
import numpy as np
import random
from random import choice as random_choice
from random import choices as random_choices
from random import uniform as random_uniform
import os
import pandas as pd
import pickle
import proximitypyhash
import pygeohash as pgh
import time


# FLAGS = flags.FLAGS

# flags.DEFINE_integer('thread', 0, 'The index of a simulation threads.')

parser = argparse.ArgumentParser(description='An implementation of argparse!')
parser.add_argument("--thread", default=0, type=int, help="0 to 600+")
parser.add_argument("--start_B", default='B', type=str, help="B or NB")
parser.add_argument("--end_B", default='B', type=str, help="B or NB")
parser.add_argument("--period", default='midday', type=str, help="choose a period")
args = parser.parse_args()

start_moment = time.time()

city_venues = pd.read_pickle("/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/Chicago_venue_info_v2.pkl")
venue_id_to_idx = pd.read_pickle('/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/Chicago_venue_id_to_idx.pkl')
midday_distances = pd.read_pickle('/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/Chicago_' + args.period + '_distances_rating_impute.pkl')
venue_to_rating = pd.read_pickle('/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/Chicago_venue_id_TO_rating_impute.pkl')
venue_b_to_rating = pd.read_pickle('/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/Chicago_venue_id_TO_rating.pkl')

# v2_b_b: [B->B, B->NB]
# v2_nb_b: [NB->B, NB->NB]
v2_b_b, v2_nb_b = pd.read_pickle('/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/chicago_' + args.period + '_business_probs.pkl')

total_threads = 20
flag_to_num_move = {
    ('B', 'B'): v2_b_b[0],
    ('B', 'NB'): v2_b_b[1],
    ('NB', 'B'): v2_nb_b[0],
    ('NB', 'NB'): v2_nb_b[1],
}
num_movements = flag_to_num_move[(args.start_B, args.end_B)]
# num_movements = len(midday_distances)//total_threads + (args.thread == total_threads-1) * len(midday_distances)%total_threads
# num_movements = 11000

sim_set_idx = 17

# prec_to_geohash = {}
prec_to_geohash_b = {}
prec_to_geohash_nb = {}
for prec in [5, 6, 7]:
    geohash_to_venue_ids = pd.read_pickle('/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/chicago_geohash_to_venue_ids_b_' +str(prec)+ '.pkl')
    prec_to_geohash_b[prec] = geohash_to_venue_ids
    geohash_to_venue_ids = pd.read_pickle('/bgfs/kpelechrinis/xil178/Documents/fcc/venues_v2/chicago_geohash_to_venue_ids_nb_' +str(prec)+ '.pkl')
    prec_to_geohash_nb[prec] = geohash_to_venue_ids

venue_ids = list(venue_id_to_idx.keys())
venue_ids_b = list(venue_b_to_rating.keys())
venue_ids_nb = list(set(venue_id_to_idx) - set(venue_b_to_rating))
start_id = random_choice(venue_ids)
venues_to_save = []
venues_to_save.append(['J', start_id])
done_movement_count = 0
linear_model = lambda x: x


def distance_to_prec(dist, dist_6_low, dist_6_high):
    prec = 7
    if dist < dist_6_low:
        prec = 7
    elif dist < dist_6_high:
        prec = 6
    else:
        prec = 5
    return prec
        
    
prec_to_delta_distances = {
    # format
    # precision: [delta_distance_min, distance_each_add, delta_distance_max]
    # the middle of each distance interval will use delta_distance_min.
    # two ends of each distance interval will use delta_distance_max.
    5: [0, 70, 70],
    6: [0, 30, 40],
    7: [0, 13, 25]
}

# # This is potentially useful
# prec_to_delta_distances = {
#     5: [0, 100, 80],
#     6: [0, 10, 20],
#     7: [0, 10, 25]
# }

print('start venue business?', args.start_B == "B")
print('end venue business?', args.end_B == "B")
    
while done_movement_count < num_movements:
    # If start_id is 'J', we will try to generate 'M' directly
    # If start_id is 'M', it has 50% prob to become a random jump
    # however, the real data may also have such continuous trajectory. So maybe we don't need this
#     if start_id[0] == 'M':
#         flag_50 = random_choice([0, 1])
#         if flag_50:
#             start_id = random_choice(venue_ids)
#             venues_to_save.append(['J', start_id])
#             print('---Find a new start id (random jump due to 50% prob)---')

    if args.start_B == 'B':
        start_id = random_choice(venue_ids_b)
    else:
        start_id = random_choice(venue_ids_nb)
    venues_to_save.append(['J', start_id])
    print('--- venue_1 business? ---', args.start_B)

    idx = venue_id_to_idx[start_id]
    lat = city_venues.iloc[idx, :]['lat']
    lng = city_venues.iloc[idx, :]['lng']
#     print('start loc', lat, ',', lng)
#     if done_movement_count == 0 or venues_to_save[-1][0] == 'M':
    sampled_distance = random_choice(midday_distances)
    print('Distance is just sampled', sampled_distance)
#     delta_distance = 50
#     distance_each_add = 25
    random_jump_flag = True
    # TODO: Maybe let delta_distance = 0 when prec==7
    dist_6_low = 1300 + 200 * random.uniform(0, 1.0)
    dist_6_high = 3000 + 1900 * random.uniform(-1.0, 1.0)
    dist_6_mid = (dist_6_low + dist_6_high)/2
    dist_7_low = 1
    dist_7_high = dist_6_low
    dist_7_mid = (dist_7_low + dist_7_high)/2
    dist_5_low = dist_6_high
    dist_5_high = 7000 + 2000 * random.uniform(-1.0, 1.0)
    dist_5_mid = (dist_5_low + dist_5_high)/2
    prec = distance_to_prec(sampled_distance, dist_6_low, dist_6_high)
    print('precision:', prec)
    delta_distance, distance_each_add, delta_distance_max = prec_to_delta_distances[prec]
    if prec == 7:
        delta_distance = delta_distance + (delta_distance_max-delta_distance)/(dist_7_high-dist_7_mid)*abs(sampled_distance-dist_7_mid)
    elif prec == 6:
        delta_distance = delta_distance + (delta_distance_max-delta_distance)/(dist_6_high-dist_6_mid)*abs(sampled_distance-dist_6_mid)
    elif prec == 5:
        delta_distance = delta_distance + (delta_distance_max-delta_distance)/(dist_5_high-dist_5_mid)*abs(sampled_distance-dist_5_mid)
    distance_add_times = 0
    while distance_add_times < 2:
#         print('sampled_distance', sampled_distance)
        small_distance = sampled_distance-delta_distance
        large_distance = sampled_distance+delta_distance
        if prec == 5:
            # TODO: This is the key to let the third peak to shift left
            small_distance -= 1500
            large_distance -= 950
#             large_distance = max(large_distance, 0.01)
        elif prec == 6:
            small_distance -= 650
            large_distance -= 450
#             large_distance = max(large_distance, 0.01)
        elif prec == 7:
            small_distance -= 400
            large_distance -= 200
            large_distance = max(large_distance, 0.01)
            if small_distance <= 0:
                # TODO: Tune this float number. Also tune the previous 3rd, 4th lines.
                # In New York City, we should not have this chunk. 
                # Thus, if Chicago distribution has problem, we can also try to remove this chunk.
                if random_uniform(0, 1) < 0.5:
                    small_distance = 0.01
                    large_distance += 100
        
        
        small_locs = proximitypyhash.get_geohash_radius_approximation(latitude=lat,longitude=lng,radius=small_distance,precision=prec)
        # TODO: using this 'large_locs' or the line after, does not make much difference. So which one should I use?
#         large_locs = proximitypyhash.get_geohash_radius_approximation(latitude=lat,longitude=lng,radius=max(large_distance, 0.001),precision=prec)
        large_locs = proximitypyhash.get_geohash_radius_approximation(latitude=lat,longitude=lng,radius=large_distance,precision=prec)
        small_set = set(small_locs)
        large_set = set(large_locs)
        ring_set = large_set - small_set
        if not ring_set:
            delta_distance += distance_each_add
            distance_add_times += 1
            print("---Need to increase distance due to no ring---")
        else:
            candidates = []
            for geoh in ring_set:
                if args.end_B == 'B':
                    geohash_to_venue_ids = prec_to_geohash_b[prec]
                else:
                    geohash_to_venue_ids = prec_to_geohash_nb[prec]
                if geoh in geohash_to_venue_ids:
                    candidates += geohash_to_venue_ids[geoh]
            if not candidates or (len(candidates) == 1 and candidates[0] == start_id):
                delta_distance += distance_each_add
                distance_add_times += 1
                print("---Need to increase distance due to no candidates---")
            else:
                num_candidates = len(candidates)
                print('# candidates:', num_candidates)
                # start_id = random_choice(candidates)
                rating_to_venues = collections.defaultdict(list)
                for cand_venue in candidates:
                    if cand_venue == start_id:
                        continue
                    rating = venue_to_rating[cand_venue]
                    rating_to_venues[rating].append(cand_venue)
                rating_set = set(rating_to_venues.keys())
                ratings = list(rating_set)
                probs = []
                for rating in ratings:
                    probs.append(linear_model(rating))
                sampled_ratings = random_choices(ratings, probs)
                sampled_rating = sampled_ratings[0]
                final_venues = rating_to_venues[sampled_rating]
                print('# rating candidates:', len(final_venues))
                start_id = random_choice(final_venues)
                venues_to_save.append(['M', start_id])
                print('---Find a new start id. Sampled distance and delta', sampled_distance, delta_distance, '---')
                random_jump_flag = False
                done_movement_count += 1
                break
    if random_jump_flag:
#         start_id = random_choice(venue_ids)
#         venues_to_save.append(['J', start_id])
        print('---did not find a dst this time---')

file_name = '/bgfs/kpelechrinis/xil178/Documents/fcc/simulations/'+str(sim_set_idx)+'/chicago_simulated_venues_' + args.period + '_' + args.start_B + '_' + args.end_B + '.pkl'
os.makedirs(os.path.dirname(file_name), exist_ok=True)
f = open(file_name, "wb")
pickle.dump(venues_to_save, f)
f.close()

end_moment = time.time()
print('Run time:', end_moment-start_moment)