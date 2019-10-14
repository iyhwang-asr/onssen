from utils import T, norm, norm_1d
from .loss_dc import loss_dc
import torch
import torch.nn.functional as F

def loss_msa(output, label):
    """
    output:
        noisy_mag: batch_size X T X F tensor
        masks: batch_size X T X F X num_speaker tensor
        clean_mags: batch_size X T X F X num_speaker tensor
    label:
        one_hot_label: the label for deep clustering
        mag_mix: the magnitude of mix speech
        mag_s1: the magnitude of clean speech s1
        mag_s2: the magnitude of clean speech s2
    """
    [embedding, mask_A, mask_B] = output
    [one_hot_label, mag_mix, mag_s1, mag_s2] = label

    # compute the loss of embedding part
    loss_embedding = loss_dc([embedding], [one_hot_label])

    #compute the loss of mask part
    loss_mask1 = norm_1d(mask_A*mag_mix - mag_s1)\
               + norm_1d(mask_B*mag_mix - mag_s2)
    loss_mask2 = norm_1d(mask_B*mag_mix - mag_s1)\
               + norm_1d(mask_A*mag_mix - mag_s2)
    loss_mask = torch.min(loss_mask1, loss_mask2)

    return loss_embedding*0.975 + loss_mask*0.025

def loss_chimera_psa(output, label):
    """
    output:
        noisy_mag: batch_size X T X F tensor
        masks: batch_size X T X F X num_speaker tensor
        clean_mags: batch_size X T X F X num_speaker tensor
    label:
        one_hot_label: the label for deep clustering
        mag_mix: the magnitude of mix speech
        mag_s1: the magnitude of clean speech s1
        mag_s2: the magnitude of clean speech s2
        cos_s1: the cosine of phase difference between mix and s1
        cos_s2: the cosine of phase difference between mix and s2
    """
    [embedding, mask_A, mask_B] = output
    [one_hot_label, mag_mix, mag_s1, mag_s2, cos_s1, cos_s2] = label

    # compute the loss of embedding part
    loss_embedding = loss_dc([embedding], [one_hot_label])
    #compute the loss of mask part
    loss_mask1 = norm_1d(mask_A*mag_mix - torch.min(mag_mix,F.relu(mag_s1*cos_s1)))\
               + norm_1d(mask_B*mag_mix - torch.min(mag_mix,F.relu(mag_s2*cos_s2)))
    loss_mask2 = norm_1d(mask_B*mag_mix - torch.min(mag_mix,F.relu(mag_s1*cos_s1)))\
               + norm_1d(mask_A*mag_mix - torch.min(mag_mix,F.relu(mag_s2*cos_s2)))
    loss_mask = torch.min(loss_mask1, loss_mask2)

    return loss_embedding*0.975 + loss_mask*0.025


def loss_mask_psa(output, label):
    """
    output:
        mask: batch_size X T X F  tensor
    label:
        mag_noisy: the magnitude of mix speech
        mag_clean: the magnitude of clean speech s1
        cos_diff: the cosine of phase difference between mix and clean
    """
    [mask] = output
    [mag_noisy, mag_clean, cos_diff] = label
    #compute the loss of mask part
    loss = norm_1d(mask * mag_noisy - torch.min(mag_noisy,F.relu(mag_clean*cos_diff)))
    return loss

def loss_mask_msa(output, label):
    """
    output:
        mask: batch_size X T X F  tensor
    label:
        mag_noisy: the magnitude of mix speech
        mag_clean: the magnitude of clean speech s1
    """
    [clean_est] = output
    [mag_clean, cos_diff] = label
    #compute the loss of mask part
    # loss = nn.MSELoss()(mask * mag_noisy, mag_clean)

    loss = torch.nn.MSELoss()(clean_est, mag_clean)
    return loss
