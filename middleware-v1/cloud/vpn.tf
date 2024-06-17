# Office VPN configuration
# ---------------------------------------
resource "aws_vpn_gateway" "vpn_gateway" {
  vpc_id = module.main-network.vpc_id

  tags = {
    Name = "${var.environment}-office-vpn-to-main-vpc"
  }
}

resource "aws_customer_gateway" "customer_gateway" {
  bgp_asn    = var.customer_gateway_asn
  ip_address = var.customer_gateway_ip
  type       = "ipsec.1"

  tags = {
    Name = "${var.environment}-office-vpn-to-main-vpc"
  }
}

resource "aws_vpn_gateway_attachment" "vpn_attachment" {
  vpc_id         = module.main-network.vpc_id
  vpn_gateway_id = aws_vpn_gateway.vpn_gateway.id
}
