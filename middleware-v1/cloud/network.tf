# Create CIDR for VPC
module "addrs" {
  source = "hashicorp/subnets/cidr"

  base_cidr_block = var.vpc_base_cidr_block
  networks = [
    {
      name     = "${var.environment}-main-private"
      new_bits = 1
    },
    {
      name     = "${var.environment}-main-public"
      new_bits = 1
    },
  ]
}

# Split CIDR for private subnets
module "private_subnets" {
  source = "hashicorp/subnets/cidr"

  base_cidr_block = lookup(module.addrs.network_cidr_blocks, "${var.environment}-main-private", null)
  networks = [
    {
      name     = "${var.environment}-main-private-00"
      new_bits = 2
    },
    {
      name     = "${var.environment}-main-private-01"
      new_bits = 2
    },
    {
      name     = "${var.environment}-main-private-02"
      new_bits = 2
    },
  ]
}

# Split CIDR for public subnets
module "public_subnets" {
  source = "hashicorp/subnets/cidr"

  base_cidr_block = lookup(module.addrs.network_cidr_blocks, "${var.environment}-main-public", null)
  networks = [
    {
      name     = "${var.environment}-main-public-00"
      new_bits = 2
    },
    {
      name     = "${var.environment}-main-public-01"
      new_bits = 2
    },
    {
      name     = "${var.environment}-main-public-02"
      new_bits = 2
    },
  ]
}

# Create VPC and subnets
module "main-network" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.5.1"

  name                                 = "${var.environment}-main"
  cidr                                 = var.vpc_base_cidr_block
  azs                                  = data.aws_availability_zones.available.names[*]
  private_subnets                      = sort(values(module.private_subnets.network_cidr_blocks))
  public_subnets                       = sort(values(module.public_subnets.network_cidr_blocks))
  enable_nat_gateway                   = true
  single_nat_gateway                   = var.deployment_profile == "development" ? true : false
  enable_dns_hostnames                 = true
  enable_dns_support                   = true
  enable_flow_log                      = true
  create_flow_log_cloudwatch_log_group = true
  create_flow_log_cloudwatch_iam_role  = true
  flow_log_max_aggregation_interval    = 60
  tags                                 = local.common_tags
}

# Attach networks to transit gateway
resource "aws_ec2_transit_gateway_vpc_attachment" "main" {
  subnet_ids         = module.main-network.private_subnets
  transit_gateway_id = data.aws_ec2_transit_gateway.main.id
  vpc_id             = module.main-network.vpc_id
  depends_on         = [module.main-network]
}

# Routes to others VPC using TGW
resource "aws_route" "main" {
  count                  = length(module.main-network.private_route_table_ids)
  route_table_id         = element(module.main-network.private_route_table_ids, count.index)
  destination_cidr_block = var.destination_cidr_block
  transit_gateway_id     = data.aws_ec2_transit_gateway.main.id
  depends_on             = [module.main-network]
}

resource "aws_route" "aladdin" {
  count                  = length(module.main-network.private_route_table_ids)
  route_table_id         = element(module.main-network.private_route_table_ids, count.index)
  destination_cidr_block = var.aladdin_cidr_block
  transit_gateway_id     = data.aws_ec2_transit_gateway.main.id
  depends_on             = [module.main-network]
}

resource "aws_route" "root" {
  count                  = length(module.main-network.private_route_table_ids)
  route_table_id         = element(module.main-network.private_route_table_ids, count.index)
  destination_cidr_block = var.root_cidr_block
  transit_gateway_id     = data.aws_ec2_transit_gateway.main.id
  depends_on             = [module.main-network]
}

resource "aws_route" "vpn" {
  count                  = length(module.main-network.private_route_table_ids)
  route_table_id         = element(module.main-network.private_route_table_ids, count.index)
  destination_cidr_block = var.vpn_cidr_block
  gateway_id             = aws_vpn_gateway.vpn_gateway.id
  depends_on             = [module.main-network]
}
