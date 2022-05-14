from verify_methods import min_entropy_from_byte_dist, odd_byte_dist_from_file, \
    plot_byte_dist, collision_blocks, chi_squared, byte_dist_from_file
import sys
from params import set_param_bool
import matplotlib.pyplot as plt

inf = sys.argv[1]
block_sizes = [32, 64, 512]
dist = byte_dist_from_file(inf, use_even=False)
even_dist = byte_dist_from_file(inf, use_even=True)
odd_dist = odd_byte_dist_from_file(inf)

print('--- min entropy ---')
min_entropy = round(min_entropy_from_byte_dist(dist), 3)
print('min-entropy for overall bytes: {}bits/byte'.format(min_entropy))
even_min_entropy = round(min_entropy_from_byte_dist(even_dist), 3)
print('min-entropy for even bytes only: {}bits/byte'.format(even_min_entropy))
odd_min_entropy = round(min_entropy_from_byte_dist(odd_dist), 3)
print('min-entropy for odd byte sonly: {}bits/byte'.format(odd_min_entropy))
print()


print('--- collisions ---')
for b in block_sizes:
    cols = collision_blocks(inf, b, use_even=False)
    print('collisions for {}-byte blocks for all bytes: {}'.format(b, cols))
print()
for b in block_sizes:
    cols = collision_blocks(inf, b, use_even=True)
    print('collisions for {}-byte blocks for even bytes: {}'.format(b, cols))
print()

print('--- chi squared ---')
chi = chi_squared(dist)
chi_stat = chi[0]
chi_pval = chi[1]
print('all bytes: chi squared statistic={} with associated p-value {}'.format(
    round(chi_stat, 2), round(chi_pval,3)))

chi = chi_squared(even_dist)
chi_stat = chi[0]
chi_pval = chi[1]
print('even bytes: chi squared statistic={} with associated p-value {}'.format(
    round(chi_stat, 2), round(chi_pval,3)))

chi = chi_squared(odd_dist)
chi_stat = chi[0]
chi_pval = chi[1]
print('odd bytes: chi squared statistic={} with associated p-value {}'.format(
    round(chi_stat, 2), round(chi_pval,3)))


# plot byte distributions
fig, ax = plt.subplots(3)

#plot_byte_dist(odd_dist, ax)
#ax.set_title('distribution of odd bytes in .wav file')

ax[0].set_title('all bytes')
plot_byte_dist(dist, ax[0])

ax[1].set_title('even bytes')
plot_byte_dist(even_dist, ax[1])

ax[2].set_title('odd bytes')
plot_byte_dist(odd_dist, ax[2])

plt.show()
