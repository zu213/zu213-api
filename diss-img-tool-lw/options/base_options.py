import argparse
import os
from util import util
import torch
import models


class BaseOptions():
    def __init__(self):
        self.initialized = False

    def initialize(self, parser):
        """This class defines options used during both training and test time.

        It also implements several helper functions such as parsing, printing, and saving the options.
        It also gathers additional options defined in <modify_commandline_options> functions in both dataset class and model class.
        """
        parser.add_argument('--dataroot', required=True, help='path to images (should have subfolders trainA, trainB, valA, valB, etc)')
        parser.add_argument('--batch_size', type=int, default=2, help='input batch size')
        parser.add_argument('--load_size', type=int, default=286, help='scale images to this size')
        parser.add_argument('--crop_size', type=int, default=256, help='then crop to this size')
        parser.add_argument('--input_nc', type=int, default=3, help='# of input image channels')
        parser.add_argument('--output_nc', type=int, default=3, help='# of output image channels')
        parser.add_argument('--nz', type=int, default=8, help='#latent vector')
        parser.add_argument('--gpu_ids', type=str, default='0', help='gpu ids: e.g. 0  0,1,2, 0,2, -1 for CPU mode')
        parser.add_argument('--name', type=str, default='', help='name of the experiment. It decides where to store samples and models')
        parser.add_argument('--preprocess', type=str, default='resize_and_crop', help='not implemented')
        parser.add_argument('--dataset_mode', type=str, default='aligned', help='aligned,single')
        parser.add_argument('--model', type=str, default='bicycle_gan', help='chooses which model to use. bicycle,, ...')
        parser.add_argument('--direction', type=str, default='AtoB', help='AtoB or BtoA')
        parser.add_argument('--epoch', type=str, default='latest', help='which epoch to load? set to latest to use latest cached model')
        parser.add_argument('--num_threads', default=4, type=int, help='# sthreads for loading data')
        parser.add_argument('--checkpoints_dir', type=str, default='./checkpoints', help='models are saved here')
        parser.add_argument('--serial_batches', action='store_true', help='if true, takes images in order to make batches, otherwise takes them randomly')
        parser.add_argument('--use_dropout', action='store_true', help='use dropout for the generator')
        parser.add_argument('--max_dataset_size', type=int, default=float("inf"), help='Maximum number of samples allowed per dataset. If the dataset directory contains more than max_dataset_size, only a subset is loaded.')
        parser.add_argument('--no_flip', action='store_true', help='if specified, do not flip the images for data argumentation')
        parser.add_argument('--basic_encode', action='store_true', help='if specified, do not flip the images for data argumentation')

        # model parameters
        parser.add_argument('--num_Ds', type=int, default=2, help='number of Discrminators')
        parser.add_argument('--netD', type=str, default='basic_256_multi', help='selects model to use for netD')
        parser.add_argument('--netD2', type=str, default='basic_256_multi', help='selects model to use for netD2')
        parser.add_argument('--netG', type=str, default='unet_256', help='selects model to use for netG')
        parser.add_argument('--netE', type=str, default='resnet_256', help='selects model to use for netE')
        parser.add_argument('--nef', type=int, default=64, help='# of encoder filters in the first conv layer')
        parser.add_argument('--ngf', type=int, default=64, help='# of gen filters in the last conv layer')
        parser.add_argument('--ndf', type=int, default=64, help='# of discrim filters in the first conv layer')
        parser.add_argument('--norm', type=str, default='instance', help='instance normalization or batch normalization')
        parser.add_argument('--upsample', type=str, default='basic', help='basic | bilinear')
        parser.add_argument('--nl', type=str, default='relu', help='non-linearity activation: relu | lrelu | elu')

        # extra parameters
        parser.add_argument('--where_add', type=str, default='all', help='input|all|middle; where to add z in the network G')
        parser.add_argument('--conditional_D', action='store_true', help='if use conditional GAN for D')
        parser.add_argument('--init_type', type=str, default='xavier', help='network initialization [normal | xavier | kaiming | orthogonal]')
        parser.add_argument('--init_gain', type=float, default=0.02, help='scaling factor for normal, xavier and orthogonal.')
        parser.add_argument('--center_crop', action='store_true', help='if apply for center cropping for the test')
        parser.add_argument('--verbose', action='store_true', help='if specified, print more debugging information')
        parser.add_argument('--suffix', default='', type=str, help='customized suffix: opt.name = opt.name + suffix: e.g., {model}_{netG}_size{load_size}')
        parser.add_argument('--display_winsize', type=int, default=256, help='display window size')
        parser.add_argument('--mod_rlhf', action='store_true',  help='My added modifications for RLHF')
        parser.add_argument('--mod_fmt', action='store_true',  help='My added modifications for FMT')

        # special tasks
        self.initialized = True
        return parser

    def parse(self):
        """Parse our options, create checkpoints directory suffix, and set up gpu device."""
        opt = self.gather_options()
        opt.isTrain = self.isTrain   # train or test

        # process opt.suffix
        if opt.suffix:
            suffix = ('_' + opt.suffix.format(**vars(opt))) if opt.suffix != '' else ''
            opt.name = opt.name + suffix

        self.print_options(opt)

        # set gpu ids
        str_ids = opt.gpu_ids.split(',')
        opt.gpu_ids = []
        for str_id in str_ids:
            id = int(str_id)
            if id >= 0:
                opt.gpu_ids.append(id)
        if len(opt.gpu_ids) > 0:
            torch.cuda.set_device(opt.gpu_ids[0])

        self.opt = opt
        return self.opt
